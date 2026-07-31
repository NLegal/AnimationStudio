from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime

from .models import ResourceSnapshot


@dataclass
class ResourceAllocation:
    allocation_id: str = ""
    task_id: str = ""
    gpu_units: int = 0
    cpu_cores: int = 0
    ram_gb: int = 0
    status: str = "active"
    started_at: str = ""
    ended_at: str = ""


class ResourceManager:
    def __init__(self, gpu_units: int = 8, cpu_cores: int = 32, ram_gb: int = 64):
        self.total_gpu = gpu_units
        self.total_cpu = cpu_cores
        self.total_ram = ram_gb
        self._allocations: dict[str, ResourceAllocation] = {}
        self._counter = 0

    def allocate(self, task_id: str, gpu: int = 0, cpu: int = 1, ram: int = 1) -> ResourceAllocation | None:
        if gpu > self.available_gpu() or cpu > self.available_cpu() or ram > self.available_ram():
            return None
        self._counter += 1
        allocation = ResourceAllocation(
            allocation_id=f"ALLOC_{self._counter}",
            task_id=task_id,
            gpu_units=gpu,
            cpu_cores=cpu,
            ram_gb=ram,
            started_at=datetime.now().isoformat(),
        )
        self._allocations[allocation.allocation_id] = allocation
        return allocation

    def release(self, allocation_id: str) -> bool:
        allocation = self._allocations.get(allocation_id)
        if allocation is None:
            return False
        allocation.status = "released"
        allocation.ended_at = datetime.now().isoformat()
        return True

    def available_gpu(self) -> int:
        used = sum(a.gpu_units for a in self._allocations.values() if a.status == "active")
        return max(self.total_gpu - used, 0)

    def available_cpu(self) -> int:
        used = sum(a.cpu_cores for a in self._allocations.values() if a.status == "active")
        return max(self.total_cpu - used, 0)

    def available_ram(self) -> int:
        used = sum(a.ram_gb for a in self._allocations.values() if a.status == "active")
        return max(self.total_ram - used, 0)

    def active_allocations(self) -> list[ResourceAllocation]:
        return [a for a in self._allocations.values() if a.status == "active"]

    def allocations_for(self, task_id: str) -> list[ResourceAllocation]:
        return [a for a in self._allocations.values() if a.task_id == task_id]

    def allocation_count(self) -> int:
        return len(self._allocations)

    def snapshot(self) -> ResourceSnapshot:
        return ResourceSnapshot(
            gpu_utilization=round((self.total_gpu - self.available_gpu()) / self.total_gpu, 2) if self.total_gpu else 0.0,
            cpu_utilization=round((self.total_cpu - self.available_cpu()) / self.total_cpu, 2) if self.total_cpu else 0.0,
            ram_used_gb=float(self.total_ram - self.available_ram()),
            timestamp=datetime.now().isoformat(),
        )

    def utilization(self) -> float:
        snapshot = self.snapshot()
        return round((snapshot.gpu_utilization + snapshot.cpu_utilization) / 2, 2)


class RenderFarm:
    def __init__(self, nodes: int = 1, gpus_per_node: int = 1):
        self.node_count = nodes
        self.gpus_per_node = gpus_per_node
        self._pending: list[str] = []
        self._rendered: list[str] = []
        self._jobs: dict[str, dict] = {}

    def total_gpus(self) -> int:
        return self.node_count * self.gpus_per_node

    def submit(self, render_id: str, job: dict | None = None) -> bool:
        if render_id in self._jobs:
            return False
        self._jobs[render_id] = job or {}
        self._pending.append(render_id)
        return True

    def render_next(self) -> str | None:
        if not self._pending:
            return None
        render_id = self._pending.pop(0)
        self._rendered.append(render_id)
        self._jobs[render_id]["status"] = "rendered"
        return render_id

    def render_all(self) -> list[str]:
        rendered = []
        while self._pending:
            rendered.append(self.render_next())
        return rendered

    def pending_count(self) -> int:
        return len(self._pending)

    def rendered_count(self) -> int:
        return len(self._rendered)

    def job(self, render_id: str) -> dict:
        return self._jobs.get(render_id, {})

    def job_status(self, render_id: str) -> str:
        return self.job(render_id).get("status", "unknown")
