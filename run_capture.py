from datetime import datetime
from os import PathLike
from pathlib import Path
import signal
from subprocess import Popen, TimeoutExpired
from typing import Any, Literal
from loguru import logger
import click
import loguru

# pacman -S python-loguru
# pacman -S python-click

Mode = Literal["preview", "save", "save_preview"]
MODE_LIST: list[Mode] = ["preview", "save", "save_preview"]
MULTICAST_ADDR = "224.0.0.123"


class DumpCommand:
    port: int
    output_path: str

    def __init__(self, port: int, output_path: PathLike | str):
        self.port = port
        self.output_path = str(output_path)

    def save_and_decode_nv_pipeline(self):
        # note that capabilties SHOULD NOT have spaces in between
        # `gst-launch-1.0` could tolerate that, but not the API itself
        return f"""gst-launch-1.0 -e udpsrc port={self.port} \
        ! 'application/x-rtp,encoding-name=H265,payload=96' \
        ! rtph265depay \
        ! h265parse \
        ! tee name=t \
        t. ! queue ! nvh265dec ! videoconvert ! autovideosink \
        t. ! queue ! mp4mux ! filesink location={self.output_path}
        """

    def save_and_decode_nv_pipeline_multicast(self):
        return f"""gst-launch-1.0 -e udpsrc port={self.port} \
            auto-multicast=true \
            multicast-group={MULTICAST_ADDR} \
        ! 'application/x-rtp,encoding-name=H265,payload=96' \
        ! rtph265depay \
        ! h265parse \
        ! tee name=t \
        t. ! queue ! vtdec_hw ! videoconvert ! autovideosink \
        t. ! queue ! mp4mux ! filesink location={self.output_path}
        """
        # `vtdec_hw` for macos
        # `nvh265dec` for nv

    def save_pipeline(self):
        return f"""gst-launch-1.0 -e udpsrc port={self.port} \
        ! 'application/x-rtp, encoding-name=H265, payload=96' \
        ! rtph265depay \
        ! queue ! h265parse ! mp4mux ! filesink location={self.output_path}
        """

    def decode_cv_only(self):
        return f"""gst-launch-1.0 -e udpsrc port={self.port} \
        ! 'application/x-rtp,encoding-name=H265,payload=96' \
        ! rtph265depay \
        ! h265parse \
        ! nvh265dec \
        ! videoconvert \
        ! autovideosink
        """

    def get_pipeline_from_mode(self, mode: Mode):
        if mode == "save":
            return self.save_pipeline()
        elif mode == "save_preview":
            return self.save_and_decode_nv_pipeline_multicast()
        elif mode == "preview":
            return self.decode_cv_only()
        raise ValueError(f"Unknown mode: {mode}")


def test_filename(
    port: int,
    output_dir: PathLike | str,
    date: datetime,
    prefix="video_",
    suffix=".mp4",
):
    date_str = date.strftime("%Y-%m-%d_%H-%M-%S")
    assert suffix.startswith("."), "suffix should start with a dot"
    file_name = f"{prefix}{date_str}_{port}{suffix}"
    return Path(output_dir) / file_name


# nmap -sS --open -p 22 192.168.2.0/24


@click.command()
@click.option("-o", "--output", type=click.Path(exists=True), default="output")
@click.option("-m", "--mode", type=click.Choice(MODE_LIST), default="save_preview")
def main(output: str, mode: Mode):
    ports = [5601, 5602, 5603, 5604, 5605, 5606]
    output_dir = Path(output)
    now = datetime.now()
    commands = [
        DumpCommand(port, test_filename(port, output_dir, now)) for port in ports
    ]
    ps: list[Popen] = []
    run_flag: bool = True

    def handle_sigint(signum: int, frame: Any):
        nonlocal run_flag
        run_flag = False
        logger.info("Received SIGINT, stopping all processes")

    for command in commands:
        p = Popen(command.get_pipeline_from_mode(mode), shell=True)
        ps.append(p)

    signal.signal(signal.SIGINT, handle_sigint)
    while run_flag:
        pass

    for p in ps:
        p.send_signal(signal.SIGINT)
    for p in ps:
        try:
            p.wait(3)
        except TimeoutExpired:
            logger.warning("Command `{}` timeout", p.args)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
