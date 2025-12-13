import asyncio
import grpc
from typing import Optional
import json
from protos import kvstore_pb2, kvstore_pb2_grpc

class KVStoreService:
    def __init__(self):
        self.prime_alive: bool = False
        self.backup_alive: bool = False
        self._running = True
        self._task: Optional[asyncio.Task] = None

        self.stub_prime = kvstore_pb2_grpc.KVStoreStub(grpc.insecure_channel('localhost:50051'))
        self.stub_backup = kvstore_pb2_grpc.KVStoreStub(grpc.insecure_channel('localhost:50052'))

        with open('data/version.json', 'r') as f:
            version_data = json.load(f)
            self.latest_version = version_data.get("latest_version", 0)

    async def start(self):
        self._task = asyncio.create_task(self._monitor_loop())

    async def stop(self):
        self._running = False
        if self._task:
            await self._task

    async def _monitor_loop(self):
        while self._running:
            try:
                self.prime_alive = await self._check_prime_status()
                self.backup_alive = await self._check_backup_status()
            except Exception as e:
                print("Error checking processes:", e)
                self.prime_alive = False
                self.backup_alive = False
            await asyncio.sleep(5)  # check every 5 seconds

    async def _check_prime_status(self) -> bool:
        try:
            prime_status_response = self.stub_prime.HealthCheck(kvstore_pb2.GrpcHealthCheckRequest())
            return prime_status_response.status
        except Exception:
            print("Prime Status Error!")
            return False

    async def _check_backup_status(self) -> bool:
        try:
            backup_status_response = self.stub_backup.HealthCheck(kvstore_pb2.GrpcHealthCheckRequest())
            return backup_status_response.status
        except Exception:
            print("Backup Status Error!")
            return False
        

    async def setData(self, key: str, value: str) -> tuple[bool, str]:
        try:
            self.latest_version += 1
            data_request = kvstore_pb2.GrpcDataRequest(
                key=key,
                data=kvstore_pb2.GrpcData(value=value, version=self.latest_version)
            )
            if self.prime_alive:
                response = self.stub_prime.SetData(data_request)
            elif self.backup_alive:
                response = self.stub_backup.SetData(data_request)
            else:
                return False, "No process is alive to save data"
            
            if response.success:
                with open('data/version.json', 'w') as f:
                    json.dump({"latest_version": self.latest_version}, f)
                return True, "Data saved successfully"
            else:
                return False, response.message
        except Exception:
            return False, "Error saving data"

    async def getData(self, key: str) -> tuple[bool, str]:
        try:
            if self.prime_alive:
                response = self.stub_prime.GetData(kvstore_pb2.GrpcDataRequest(key=key))
            elif self.backup_alive:
                response = self.stub_backup.GetData(kvstore_pb2.GrpcDataRequest(key=key))
            else:
                return False, "No process is alive to get data"
            
            if response.success:
                return True, response.data.value
            else:
                return False, response.message
        except Exception:
            return False, "Error getting data"

    async def deleteData(self, key: str) -> bool:
        try:
            if self.prime_alive:
                response = self.stub_prime.DeleteData(kvstore_pb2.GrpcDataRequest(key=key))
            elif self.backup_alive:
                response = self.stub_backup.DeleteData(kvstore_pb2.GrpcDataRequest(key=key))
            else:
                return False, "No process is alive to delete data"

            if response.success:
                return True, "Data deleted successfully"
            else:
                return False, response.message
        except Exception:
            return False, "Error deleting data"

kvstore_service = KVStoreService()