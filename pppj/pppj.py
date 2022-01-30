"""This should provide a parsl provider (parsl.providers.provider_base.ExecutionProvider)
that delegates work to a psij executor.
"""

import logging

logger = logging.getLogger("parsl.pppj")

print("importing pppj")

import shlex

from typing import Any, Dict, List, Optional

from parsl.providers.provider_base import ExecutionProvider, JobState
from parsl.providers.provider_base import JobState as parsl_JobState
from parsl.providers.provider_base import JobStatus as parsl_JobStatus
from parsl.launchers.launchers import Launcher

from psij import Job, JobAttributes, JobExecutor, ResourceSpec, JobSpec, UnreachableStateException
from psij import JobState as psij_JobState

print("imported pppj")


psij_state_to_parsl_status = {
    psij_JobState.NEW._value_: parsl_JobState.PENDING,
    psij_JobState.QUEUED._value_: parsl_JobState.PENDING,
    psij_JobState.ACTIVE._value_: parsl_JobState.RUNNING,
    psij_JobState.COMPLETED._value_: parsl_JobState.COMPLETED,
    psij_JobState.FAILED._value_: parsl_JobState.FAILED,
    psij_JobState.CANCELED._value_: parsl_JobState.CANCELLED  # haha empire vs us spelling
  }

class PsiJProvider(ExecutionProvider):

    def __init__(
        self, *,
        job_executor: JobExecutor,  # j/psi executor that should do the work
        job_attributes: Optional[JobAttributes] = None, # TODO: is it safe to re-use job attributes between jobs?
        job_resources: Optional[ResourceSpec] = None, # TODO: likewise is it safe to re-use job resources?
        init_blocks: int,
        min_blocks: int,
        max_blocks: int,
        nodes_per_block: int,   # TODO see my notes on parsl bug that this isn't documented
        launcher: Launcher, # parsl launcher
        job_launcher: Optional[str] = None, # psi j launcher
        parallelism: float
      ):
        self.job_executor = job_executor
        self.job_attributes = job_attributes
        self.job_launcher = job_launcher
        self.job_resources = job_resources
        self.nodes_per_block = nodes_per_block
        self.init_blocks = init_blocks
        self.min_blocks = min_blocks
        self.max_blocks = max_blocks
        self.parallelism = parallelism

        self.resources: Dict[Any, Any]
        self.resources = {} # undocumented requirement from elsewhere in parsl: used to acquire job IDs from keys, but apparently the value is not inspected. so the value can be whatever the provider wants.

        super().__init__()

    status_polling_interval = 60
    label = "psij"  # TODO: could be based on the psij provider name?

    def submit(self, command: str, tasks_per_node: int, job_name: str = "parsl.auto") -> str:
        logger.info(f"submitting, command is {command}")
        assert tasks_per_node == 1  # this is basically a parsl unfeature now (c.f. ipp deprecation) but it could probbably be implemented as part of the jobspec?
        # TODO: use job name in jobspec somewhere
        split = shlex.split(command)
        job = Job(JobSpec(executable=split[0], arguments=split[1:], attributes=self.job_attributes, launcher=self.job_launcher, resources=self.job_resources))
        self.job_executor.submit(job)
        # submit needs to return a suitable job ID (that will be aligned with `status` job_ids input)
        # so it needs to be in harmony with the status call.
        # for now use .getId - other options are: assign and bind to job objects at the provider level; use native ID.
        self.resources[job.id] = job  # trusts psij to give unique job IDs
        logger.info(f"submitted {job.id}")
        return job.id


    def cancel(self, job_ids: List[str]) -> List[bool]:
        logger.info(f"Calling cancel for job ids {job_ids}")
        results = []

        for job_id in job_ids:
            job = self.resources[job_id]
            logger.info(f"Calling cancel for job id {job_id}")
            job.cancel()
            logger.info(f"Called cancel for job id {job_id}")

        for job_id in job_ids:
            job = self.resources[job_id]
            try:
                logger.info(f"Waiting for CANCELED state for job id {job_id}")
                r = job.wait(target_states=[psij_JobState.CANCELED])
                # what are the possible outputs here and what I'm expecting?
                assert r is not None, "job.wait should not report that a timeout was reached"
                assert r.state == psij_JobState.CANCELED, "job.wait should return a CANCELLED state"
                assert r.final, "job.wait should return a final state"
                logger.info(f"Got to CANCELED state for job id {job_id}")
                result = True
            except UnreachableStateException:
                logger.info(f"Got UnreachableStateException waiting for CANCELED state for job id {job_id}")
                result = False
            results.append(result)

        logger.info("All cancels completed")
        return results

    def status(self, job_ids: List[Any]) -> List[parsl_JobStatus]:
        logger.info("Polling status")
        statuses = []
        for key in job_ids:
            job = self.resources[key]  # part of the provider status contract is not asked for statuses for IDs that weren't returned by submit. TODO: document that more explicitly in the parsl docstrings if that isn't already written.

            # assign to a variable so that we can compare it repeatedly without it changing
            status = job.status 

            state = status.state._value_
            # the _value_ here is because JobState cannot be used as a dictionary key as unhashable

            logger.info(f"job {job.id} status {job.status}")
            job_status = parsl_JobStatus(
                state = psij_state_to_parsl_status[state],
                message = status.message,
                exit_code = status.exit_code,
                stdout_path = None,  # TODO: where do these come from in other providers?
                stderr_path = None
                )
            statuses.append(job_status)
        return statuses
