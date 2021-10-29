import subprocess, pathlib
from subprocess import Popen
from pathlib import Path
import uuid

from vlctelnet import *

import settings


class VLCProcess(Popen):
    path: Path
    host: str
    port: int
    password: uuid.UUID
    
    def __init__ (self, *args, **kwargs):
        self.path = settings.current['vlc-telnet']['path']
        self.host = settings.current['vlc-telnet']['telnet-host']
        self.port = int(settings.current['vlc-telnet']['telnet-port'])
        self.password = str(uuid.uuid4()).replace('-', "_")
        
        super().__init__(
            [
                self.path,
                # f"--intf telnet",
                # f"-I telnet",
                f"--extraintf=telnet",
                f"--telnet-host={self.host}",
                f"--telnet-port={self.port}",
                f"--telnet-password={self.password}"
            ]
        )
    
    def get_telnet_control(self) -> VLCTelnet:
        return VLCTelnet(
            host=self.host,
            port=self.port,
            password=str(self.password)
        )