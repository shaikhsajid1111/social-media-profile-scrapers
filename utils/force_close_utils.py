import subprocess
from typing import Set, List
import os
import signal


class ForceProcessCloseUtils:
    @staticmethod
    def extract_processes_pids(process_name: str) -> Set[str]:
        pids = []
        try:
            command = ["pgrep", "-f", process_name]
            output = subprocess.check_output(command)
            pids = output.decode().strip().split()
            return set(pids)
        except Exception as ex:
            print(f"Error while extracting processes pid's {ex}")

    def force_close_processes(spawned_ids: List[str]):
        for pid in spawned_ids:
            try:
                assert pid is not None
                os.kill(int(pid), signal.SIGKILL)
            except Exception as ex:
                print(f"Error while force killing the process with pid : {pid}: {ex}")
                ForceProcessCloseUtils.force_close_processes_using_subprocess([pid])

    def force_close_processes_using_subprocess(spawned_ids: List[str]):
        for pid in spawned_ids:
            try:
                command = ["kill", "-9", pid]
                subprocess.run(
                    command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception as ex:
                print(f"Error while force closing the process with pid: {pid}: {ex}")