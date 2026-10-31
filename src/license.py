import os
import json
import time

LICENSE_VERSION = "1.0"

LICENSE_TEXT = """END-USER LICENSE AGREEMENT & DISCLAIMER OF LIABILITY (EULA)
============================================================
PORT VIEWER • OPEN-SOURCE EDUCATIONAL SOFTWARE
VERSION 1.0

IMPORTANT — READ CAREFULLY BEFORE INSTALLING OR RUNNING:
By installing, downloading, copying, accessing, or running Port Viewer
("the Software"), you explicitly acknowledge and agree to be bound by
the terms and conditions set forth below. If you do not agree to every
term in this agreement, you must NOT install, run, or use this software.

1. PURPOSE: EDUCATIONAL, RESEARCH & SOLO STUDY USE ONLY
The Software is provided strictly and solely for personal study, academic
research, individual educational testing, and solo experimentation.
It is an open-source project intended to demonstrate network socket
inspection and process management in Windows environments.

2. AT USER'S OWN RISK & INDEPENDENT SELF-DECISION
You expressly understand, acknowledge, and agree that:
  a) All use, execution, and operation of the Software is conducted at
     your OWN EXCLUSIVE RISK, discretion, and self-decision.
  b) Inspecting network ports and terminating processes (PID termination)
     can lead to loss of unsaved work, disruption of background services,
     network disconnects, or operating system instability if misused.
  c) You are solely responsible for determining the safety, identity,
     and importance of any process before choosing to terminate it.
  d) You alone bear all responsibility for any consequences, data loss,
     or system impact resulting from your use of this Software.

3. ABSOLUTE DISCLAIMER OF WARRANTIES ("AS IS")
THE SOFTWARE IS PROVIDED "AS IS" AND "AS AVAILABLE", WITHOUT WARRANTY OF
ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE,
ACCURACY, QUIET ENJOYMENT, SYSTEM INTEGRATION, OR NON-INFRINGEMENT.
THE ENTIRE RISK AS TO THE QUALITY, PERFORMANCE, AND ACCURACY OF THE
SOFTWARE IS WITH YOU.

4. COMPLETE LIMITATION OF LIABILITY & ZERO BLAME CLAUSE
TO THE MAXIMUM EXTENT PERMITTED UNDER APPLICABLE LAW, IN NO EVENT SHALL
THE AUTHOR, DEVELOPER, CONTRIBUTORS, COPYRIGHT HOLDERS, OR DISTRIBUTORS
BE BLAMED, ACCUSED, HELD LIABLE, PROSECUTED, SUED, OR SUBJECT TO ANY
CLAIM, ACTION, PROCEEDING, OR PENALTY FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, PUNITIVE, OR CONSEQUENTIAL DAMAGES WHATSOEVER (INCLUDING,
WITHOUT LIMITATION, DAMAGES FOR LOSS OF BUSINESS, LOSS OF DATA, COMPUTER
FAILURE OR MALFUNCTION, CORRUPTION OF FILES, WORK STOPPAGE, SYSTEM CRASHES,
OR ANY OTHER PECUNIARY LOSS) ARISING OUT OF OR IN CONNECTION WITH THE
SOFTWARE, ITS INSTALLATION, EXECUTION, MISUSE, OR INABILITY TO USE, EVEN
IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

5. INDEMNIFICATION & HOLD HARMLESS
You agree to indemnify, defend, and hold completely harmless the author,
creator, and contributors from and against any and all claims, liabilities,
demands, damages, losses, costs, and expenses (including legal fees)
arising out of or relating to your use, misuse, distribution, or violation
of these terms.

6. ACCEPTANCE BY AFFIRMATIVE ACTION
By clicking "I Agree & Continue", you confirm that you have read this
entire agreement, understand all terms, agree that this software is for
study/solo use at your own risk, and waive any right to hold the author
or contributors liable for any reason under any jurisdiction.
"""

def get_config_dir() -> str:
    """Returns the persistent user configuration directory."""
    appdata = os.environ.get("APPDATA")
    if appdata and os.path.exists(appdata):
        target = os.path.join(appdata, "PortViewer")
    else:
        target = os.path.join(os.path.expanduser("~"), ".port_viewer")
    os.makedirs(target, exist_ok=True)
    return target

def get_license_file_path() -> str:
    """Returns the path to the license acceptance file."""
    return os.path.join(get_config_dir(), "license_accepted.json")

def has_accepted_license() -> bool:
    """Checks whether the user has previously accepted the license agreement."""
    file_path = get_license_file_path()
    if not os.path.exists(file_path):
        return False
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return (
                data.get("accepted") is True
                and data.get("version") == LICENSE_VERSION
            )
    except Exception:
        return False

def set_accepted_license(accepted: bool = True) -> None:
    """Records the user's acceptance or revocation of the license agreement."""
    file_path = get_license_file_path()
    try:
        data = {
            "accepted": accepted,
            "version": LICENSE_VERSION,
            "timestamp": time.time(),
            "formatted_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "terms": "Educational & Solo Study Use Only - At User's Own Risk"
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save license agreement: {e}")

def get_license_text() -> str:
    """Returns the full license and disclaimer text."""
    return LICENSE_TEXT.strip()
