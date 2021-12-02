from pppj.pppj import PsiJProvider

# imports for monitoring:
from parsl.monitoring import MonitoringHub

import os

from parsl.providers import LocalProvider
from parsl.channels import LocalChannel
from parsl.launchers import SimpleLauncher

from parsl.config import Config
from parsl.executors import HighThroughputExecutor


from parsl.data_provider.http import HTTPInTaskStaging
from parsl.data_provider.ftp import FTPInTaskStaging
from parsl.data_provider.file_noop import NoOpFileStaging

working_dir = os.getcwd() + "/" + "test_htex_alternate"

from psij import JobExecutor, JobAttributes, ResourceSpecV1

# i got this "get_instance" call from the test suite. Is it the
# official way in which I should be getting the instance?
# Why do I need a name if the URL identifies how to submit already
# Is this a leak of a SAGA parameter into the new API?
jex = JobExecutor.get_instance(name='slurm', url=None)
jattr = JobAttributes(custom_attributes={"slurm.constraint":"knl"})
jlaunch = "srun"
jresources = ResourceSpecV1(exclusive_node_use=True, node_count=3)

def fresh_config():
    return Config(
        executors=[
            HighThroughputExecutor(
                label="htex_psij_local",
                working_dir=working_dir,
                storage_access=[FTPInTaskStaging(), HTTPInTaskStaging(), NoOpFileStaging()],
                worker_debug=True,
                cores_per_worker=1,
                heartbeat_period=2,
                heartbeat_threshold=5,
                poll_period=100,
                provider=PsiJProvider(
                    job_executor=jex,
                    job_attributes=jattr,
                    job_launcher=jlaunch,
                    job_resources=jresources,
                    init_blocks=0,
                    min_blocks=0,
                    max_blocks=1,
                    nodes_per_block=1,
                    launcher=SimpleLauncher(),
                    parallelism=1
                ),
            )
        ],
        strategy='simple',
        app_cache=True, checkpoint_mode='task_exit',
        retries=2
    )


config = fresh_config()

