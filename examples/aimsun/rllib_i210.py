"""
Load an already existing Aimsun template and run the simulation
"""

from flow.core.experiment import Experiment
from flow.core.params import AimsunParams, EnvParams, NetParams
from flow.core.params import VehicleParams
from flow.envs import TestEnv
from flow.scenarios.loop import Scenario
from flow.controllers.rlcontroller import RLController

import json

import ray
try:
    from ray.rllib.agents.agent import get_agent_class
except ImportError:
    from ray.rllib.agents.registry import get_agent_class
from ray.tune import run_experiments
from ray.tune.registry import register_env

from flow.utils.registry import make_create_env
from flow.utils.rllib import FlowParamsEncoder
from flow.core.params import SumoParams, EnvParams, InitialConfig, NetParams
from flow.core.params import VehicleParams
from flow.controllers import RLController, IDMController, ContinuousRouter


# time horizon of a single rollout
HORIZON = 1000  # 3000
# number of rollouts per training iteration
N_ROLLOUTS = 2  # 20
# number of parallel workers
N_CPUS = 1  # 2


vehicles = VehicleParams()
# vehicles.add(
#     veh_id="rl",
#     acceleration_controller=(RLController, {}),
#     num_vehicles=2000
# )



flow_params = dict(
    # name of the experiment
    exp_tag="test",

    # name of the flow environment the experiment is running on
    env_name="TestEnv",

    # name of the scenario class the experiment is running on
    scenario="Scenario",

    # simulator that is used by the experiment
    simulator='traci',
    # simulator='aimsun',

    # sumo-related parameters (see flow.core.params.SumoParams)
    sim=AimsunParams(
        sim_step=0.1,
        render=True,
        emission_path='data'),
    #     scenario_name="Dynamic Scenario 866",
        # replication_name="Replication 930",
        # centroid_config_name="Centroid Configuration 910"),
    # ),
        # subnetwork_name="Subnetwork 8028981"),
    


    # environment related parameters (see flow.core.params.EnvParams)
    env=EnvParams(),

    # network-related parameters (see flow.core.params.NetParams and the
    # scenario's documentation or ADDITIONAL_NET_PARAMS component)
    # net=NetParams(template="/Users/nathan/internship/ring.ang"),
    net=NetParams(template="/Users/nathan/internship/small_test/small_test.ang"),

    # vehicles to be placed in the network at the start of a rollout (see
    # flow.core.vehicles.Vehicles)
    veh=vehicles,

    # parameters specifying the positioning of vehicles upon initialization/
    # reset (see flow.core.params.InitialConfig)
    initial=InitialConfig(),
)



def setup_exps():

    alg_run = "PPO"

    agent_cls = get_agent_class(alg_run)
    config = agent_cls._default_config.copy()
    config["num_workers"] = N_CPUS
    config["train_batch_size"] = HORIZON * N_ROLLOUTS
    config["gamma"] = 0.999  # discount rate
    config["model"].update({"fcnet_hiddens": [16, 16]})
    config["use_gae"] = True
    config["lambda"] = 0.97
    config["kl_target"] = 0.02
    config["num_sgd_iter"] = 10
    config['clip_actions'] = False  # FIXME(ev) temporary ray bug
    config["horizon"] = HORIZON

    # save the flow params for replay
    flow_json = json.dumps(
        flow_params, cls=FlowParamsEncoder, sort_keys=True, indent=4)
    config['env_config']['flow_params'] = flow_json
    config['env_config']['run'] = alg_run

    create_env, gym_name = make_create_env(params=flow_params, version=0)
    env = create_env()
    # Register as rllib env
    # register_env(gym_name, create_env)
    return alg_run, gym_name, config, env



from softlearning.misc.utils import deep_update
from ray import tune
import numpy as np

M = 256
REPARAMETERIZE = True

DEFAULT_MAX_PATH_LENGTH = 1000
DEFAULT_NUM_EPOCHS = 200
NUM_CHECKPOINTS = 10

GAUSSIAN_POLICY_PARAMS = {
    'type': 'GaussianPolicy',
    'kwargs': {
        'hidden_layer_sizes': (M, M),
        'squash': True,
    }
}

ALGORITHM_PARAMS = {
    'type': 'SAC',

    'kwargs': {
        'n_epochs': 200,
        'epoch_length': 1000,
        'train_every_n_steps': 1,
        'n_train_repeat': 1,
        'eval_render_mode': None,
        'eval_n_episodes': 1,
        'eval_deterministic': True,
        'discount': 0.99,
        'tau': 5e-3,
        'reward_scale': 1.0,
        'reparameterize': REPARAMETERIZE,
        'lr': 3e-4,
        'target_update_interval': 1,
        'target_entropy': 'auto',
        'store_extra_policy_info': False,
        'action_prior': 'uniform',
        'n_initial_exploration_steps': int(1e3),
    }
}

def get_variant_spec_base():
    variant_spec = {
        # 'git_sha': get_git_rev(__file__),
        'flow_params': flow_params,        
        'environment_params': {
            'training': {
                'kwargs': {
                    # Add environment params here
                },
            },
            'evaluation': tune.sample_from(lambda spec: (
                spec.get('config', spec)
                ['environment_params']
                ['training']
            )),
        },
        'policy_params': GAUSSIAN_POLICY_PARAMS,
        'Q_params': {
            'type': 'double_feedforward_Q_function',
            'kwargs': {
                'hidden_layer_sizes': (M, M),
            }
        },
        'algorithm_params': ALGORITHM_PARAMS,
        'replay_pool_params': {
            'type': 'SimpleReplayPool',
            'kwargs': {
                'max_size': tune.sample_from(lambda spec: (
                    {
                        'SimpleReplayPool': int(1e6),
                        'TrajectoryReplayPool': int(1e4),
                    }.get(
                        spec.get('config', spec)
                        ['replay_pool_params']
                        ['type'],
                        int(1e6))
                )),
            }
        },
        'sampler_params': {
            'type': 'SimpleSampler',
            'kwargs': {
                'max_path_length': DEFAULT_MAX_PATH_LENGTH,
                'min_pool_size': DEFAULT_MAX_PATH_LENGTH,
                'batch_size': 256,
            }
        },
        'run_params': {
            'seed': tune.sample_from(
                lambda spec: np.random.randint(0, 10000)),
            'checkpoint_at_end': True,
            'checkpoint_frequency': DEFAULT_NUM_EPOCHS // NUM_CHECKPOINTS,
            'checkpoint_replay_pool': False,
        },
    }

    return variant_spec

variant_spec = get_variant_spec_base()

from exprunner import ExperimentRunner

import multiprocessing
from softlearning.misc.utils import datetimestamp

def generate_experiment_kwargs(variant_spec):
    local_dir = '~/ray_results/SAC_tmp/'

    resources_per_trial = {}
    resources_per_trial['cpu'] = 1#multiprocessing.cpu_count()
    resources_per_trial['gpu'] = 0#None
    resources_per_trial['extra_cpu'] = 0#None
    resources_per_trial['extra_gpu'] = 0#None

    datetime_prefix = datetimestamp()
    experiment_id = '-'.join((datetime_prefix, 'experiment_name'))

    def create_trial_name_creator(trial_name_template=None):
        if not trial_name_template:
            return None

        def trial_name_creator(trial):
            return trial_name_template.format(trial=trial)

        return tune.function(trial_name_creator)

    experiment_kwargs = {
        'name': experiment_id,
        'resources_per_trial': resources_per_trial,
        'config': variant_spec,
        'local_dir': local_dir,
        'num_samples': 1,
        'upload_dir': '',
        'checkpoint_freq': (
            variant_spec['run_params']['checkpoint_frequency']),
        'checkpoint_at_end': (
            variant_spec['run_params']['checkpoint_at_end']),
        'trial_name_creator': create_trial_name_creator(
            'id={trial.trial_id}-seed={trial.config[run_params][seed]}'),
        'restore': None,
    }

    return experiment_kwargs

if __name__ == "__main__":
    # alg_run, gym_name, config, env = setup_exps()

    trainable_class = ExperimentRunner

    experiment_kwargs = generate_experiment_kwargs(variant_spec)

    print("\n\nEXPERIMENT_KWARGS", experiment_kwargs, "\n\n\n")

    print("ray.init()")

    ray.init(
        num_cpus=N_CPUS, num_gpus=0, resources={}, local_mode=False,
        )#include_webui=True, temp_dir='~/tmp_tmp')#,
        # resources=example_args.resources or {},
        # local_mode=local_mode,
        # include_webui=example_args.include_webui, TODO
        # temp_dir=example_args.temp_dir)

    print("tune.run()")

    tune.run(
        trainable_class,
        **experiment_kwargs,
        with_server=False,
        server_port=9898,
        scheduler=None,
        reuse_actors=True)

    print("--end--")

