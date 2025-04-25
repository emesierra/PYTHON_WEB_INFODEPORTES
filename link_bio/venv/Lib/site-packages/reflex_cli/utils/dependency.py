"""Building the app and initializing all prerequisites."""

from __future__ import annotations

import io
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from reflex_cli import constants
from reflex_cli.utils import console


def detect_encoding(filename: Path) -> str | None:
    """Detect the encoding of the given file.

    Args:
        filename: The file to detect encoding for.

    Raises:
        FileNotFoundError: If the file `filename` does not exist.

    Returns:
        The encoding of the file if file exits and encoding is detected, otherwise None.

    """
    if not filename.exists():
        raise FileNotFoundError

    for encoding in [
        None if sys.version_info < (3, 10) else io.text_encoding(None),
        "utf-8",
    ]:
        try:
            filename.read_text(encoding)
        except UnicodeDecodeError:  # noqa: PERF203
            continue
        except Exception:
            return None
        else:
            return encoding
    else:
        return None


def check_requirements():
    """Check if the requirements.txt needs update based on current environment.
    Throw warnings if too many installed or unused (based on imports) packages in
    the local environment.

    Returns:
        None

    Raises:
        SystemExit: If no requirements.txt is found.

    """
    # First check the encoding of requirements.txt if applicable. If unable to determine encoding
    # will not proceed to check for requirement updates.
    encoding = "utf-8"
    if (
        Path(constants.RequirementsTxt.FILE).exists()
        and (encoding := detect_encoding(Path(constants.RequirementsTxt.FILE))) is None
    ):
        return

    # Run the pipdeptree command and get the output
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as cpe:
        console.debug(f"Unable to run pip freeze in subprocess: {cpe}")
        console.warn(
            "Unable to detect installed packages in your environment using pip freeze."
            " Please make sure your requirements.txt is up to date."
        )
        return

    # Filter the output lines using a regular expression
    lines = result.stdout.split("\n")
    new_requirements_lines: set[str] = set()
    for line in lines:
        if re.match(r"^\w+", line):
            new_requirements_lines.add(f"{line}\n")

    current_requirements_lines: set[str] = set()
    if Path(constants.RequirementsTxt.FILE).exists():
        with Path(constants.RequirementsTxt.FILE).open(encoding=encoding) as f:
            current_requirements_lines = set(f)
            console.debug("Current requirements.txt:")
            console.debug("".join(current_requirements_lines))

    diff = list(new_requirements_lines - current_requirements_lines)

    if not diff:
        return

    if not current_requirements_lines:
        console.warn("It seems like there's no requirements.txt in your project.")
        raise SystemExit("No requirements.txt found.")

    console.warn("Detected difference in requirements.txt and python env.")
    console.warn("The requirements.txt may need to be updated.")
    console.ask("Do you wish to proceed? (ctl+c to cancel)")
    return


def match_reflex_package(package: str) -> str | None:
    """Match the reflex package in the requirements.txt file.

    Args:
        package: The package line to match.

    Returns:
        The reflex version if found, otherwise None.

    """
    pattern = r"^reflex\s*==\s*([\d\.]+)$"
    match = re.match(pattern, package)
    if match:
        return (match.group(1) or match.group(2) or "").replace(" ", "")
    return None


def get_reflex_version() -> str:
    """Extract the reflex version from the requirements.txt file.

    Returns:
        The reflex version if found, otherwise the latest version.

    """
    try:
        requirements_path = Path("requirements.txt")
        if not requirements_path.exists():
            console.warn(
                "requirements.txt file does not exist. Reflex version is unknown."
            )
            return "unknown"
        with requirements_path.open("r") as file:
            for line in file:
                if version := match_reflex_package(line):
                    return version
            return "unknown"
    except Exception as ex:
        console.warn(
            f"Unable to read reflex version from requirements.txt due to: {ex}. Reflex version is unknown."
        )
    return "unknown"


def is_valid_url(url: str) -> bool:
    """Check if the given URL is valid.

    Args:
        url: The URL to check.

    Returns:
        True if the URL is valid, otherwise False.

    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def extract_domain(url: str) -> str:
    """Extract the domain from the given URL.

    Args:
        url: The URL to extract the domain from.

    Returns:
        The domain part of the url.

    """
    parsed_url = urlparse(url)
    return parsed_url.netloc
