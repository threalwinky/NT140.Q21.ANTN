from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import Switch
from mininet.topo import Topo

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BMV2_ROOT = PROJECT_ROOT / "SISTAR" / "BMv2"
TOOLS_DIR = BMV2_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from cli_templates import HOSTS

THRIFT_PORTS = {"s1": 9090, "s2": 9091, "s3": 9092}


class BMv2Switch(Switch):
    def __init__(self, name: str, json_path: str, thrift_port: int, log_dir: str, behavioral_exe: str, device_id: int, **kwargs):
        super().__init__(name, **kwargs)
        self.json_path = Path(json_path)
        self.thrift_port = thrift_port
        self.log_dir = Path(log_dir)
        self.behavioral_exe = behavioral_exe
        self.device_id = device_id
        self.pid_file = self.log_dir / f"{self.name}.pid"
        self.log_file = self.log_dir / f"{self.name}.log"

    def start(self, controllers):
        self.log_dir.mkdir(parents=True, exist_ok=True)
        interfaces = []
        for port, intf in sorted(self.intfs.items()):
            if port == 0 or not intf.name:
                continue
            interfaces.extend(["-i", f"{port}@{intf.name}"])

        command = [
            self.behavioral_exe,
            "--device-id",
            str(self.device_id),
            "--thrift-port",
            str(self.thrift_port),
            *interfaces,
            str(self.json_path),
        ]
        shell_command = " ".join(shlex.quote(part) for part in command)
        self.cmd(f"{shell_command} > {shlex.quote(str(self.log_file))} 2>&1 & echo $! > {shlex.quote(str(self.pid_file))}")

    def stop(self, deleteIntfs=True):
        pid_path = shlex.quote(str(self.pid_file))
        self.cmd(f"if [ -f {pid_path} ]; then kill $(cat {pid_path}) >/dev/null 2>&1; rm -f {pid_path}; fi")
        super().stop(deleteIntfs=deleteIntfs)


class SistarLabTopo(Topo):
    def build(self, json_path: str, log_dir: str, behavioral_exe: str):
        h1 = self.addHost("h1", ip=f"{HOSTS['h1']['ip']}/8", mac=HOSTS["h1"]["mac"])
        h2 = self.addHost("h2", ip=f"{HOSTS['h2']['ip']}/8", mac=HOSTS["h2"]["mac"])
        h3 = self.addHost("h3", ip=f"{HOSTS['h3']['ip']}/8", mac=HOSTS["h3"]["mac"])

        s1 = self.addSwitch("s1", cls=BMv2Switch, json_path=json_path, thrift_port=9090, log_dir=log_dir, behavioral_exe=behavioral_exe, device_id=0)
        s2 = self.addSwitch("s2", cls=BMv2Switch, json_path=json_path, thrift_port=9091, log_dir=log_dir, behavioral_exe=behavioral_exe, device_id=1)
        s3 = self.addSwitch("s3", cls=BMv2Switch, json_path=json_path, thrift_port=9092, log_dir=log_dir, behavioral_exe=behavioral_exe, device_id=2)

        self.addLink(h1, s1, port2=1)
        self.addLink(h2, s2, port2=1)
        self.addLink(s1, s3, port1=2, port2=1)
        self.addLink(s2, s3, port1=2, port2=2)
        self.addLink(h3, s3, port2=3)


def _require_root() -> None:
    if os.geteuid() != 0:
        raise SystemExit("Run this script with sudo because Mininet and BMv2 need root privileges")


def _require_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"Required command not found: {name}")


def _compile_p4(p4c: str, p4_path: Path, json_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([p4c, "--p4v", "16", "-o", str(json_path), str(p4_path)], check=True)


def _load_switch_commands(cli: str, commands_dir: Path) -> None:
    time.sleep(1.0)
    for switch_name, thrift_port in THRIFT_PORTS.items():
        command_file = commands_dir / f"{switch_name}_commands.cli"
        if not command_file.exists():
            raise FileNotFoundError(f"Missing CLI command file: {command_file}")
        with command_file.open("rb") as stdin:
            subprocess.run([cli, "--thrift-port", str(thrift_port)], stdin=stdin, check=True)


def _configure_hosts(net: Mininet) -> None:
    for host_name, host_info in HOSTS.items():
        host = net.get(host_name)
        host.cmd(f"ip route replace 10.0.0.0/8 dev {host.defaultIntf()}")
        for peer_name, peer_info in HOSTS.items():
            if peer_name != host_name:
                host.setARP(peer_info["ip"], peer_info["mac"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SISTAR BMv2 Mininet lab")
    parser.add_argument("--p4", type=Path, default=BMV2_ROOT / "DT.p4")
    parser.add_argument("--json", type=Path, default=BMV2_ROOT / "generated" / "DT.json")
    parser.add_argument("--commands-dir", type=Path, default=BMV2_ROOT / "generated")
    parser.add_argument("--log-dir", type=Path, default=BMV2_ROOT / "generated" / "logs")
    parser.add_argument("--p4c", default="p4c-bm2-ss")
    parser.add_argument("--behavioral-exe", default="simple_switch")
    parser.add_argument("--cli", default="simple_switch_CLI")
    parser.add_argument("--no-compile", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    _require_root()
    _require_tool(args.behavioral_exe)
    _require_tool(args.cli)
    if not args.no_compile:
        _require_tool(args.p4c)
        _compile_p4(args.p4c, args.p4, args.json)

    topo = SistarLabTopo(json_path=str(args.json), log_dir=str(args.log_dir), behavioral_exe=args.behavioral_exe)
    net = Mininet(topo=topo, controller=None, link=TCLink, autoSetMacs=False, autoStaticArp=False)

    try:
        net.start()
        _configure_hosts(net)
        _load_switch_commands(args.cli, args.commands_dir)
        print("SISTAR BMv2 lab is ready.")
        print("Try: h3 python3 SISTAR/BMv2/lab/receiver.py --duration 60")
        print("Try: h1 python3 SISTAR/BMv2/lab/traffic_generator.py --mode benign --dst 10.0.3.3 --count 20 --pps 2")
        print("Try: h2 python3 SISTAR/BMv2/lab/traffic_generator.py --mode attack-lab --dst 10.0.3.3 --count 200 --pps 20 --i-understand-this-is-mininet-only")
        CLI(net)
    finally:
        net.stop()


if __name__ == "__main__":
    main()
