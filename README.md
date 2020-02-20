# JOYSTICK 
The ATT&CK Evaluations results data contains a wealth of information to allow readers to better understand how capabilities work. At the same time, we recognize that getting a quick, high level understanding of a tool’s performance is difficult. To address this, we developed and released Joystick, an ATT&CK Evaluations data analysis tool.​

## Requirements
- [python3](https://www.python.org/) (3.7+)
- Google Chrome is our only supported/tested browser

## Installation
Start by cloning this repository.
```
git clone https://github.com/mitre-attack/joystick.git
```
From the root of this project, install the PIP requirements.
```
pip install -r requirements.txt
```
Then start the server.
```
python joystick.py
```
Once the server has started, point your browser to localhost:8000, and start browsing through evaluation results.

## Intended Use
Please note that Joystick is currently intended to be used as a local, single user application. 

## How do I contribute?

We welcome all the help we can get in making Joystick a more useful tool for the community. We have made a working prototype and acknowledge that there will need to be increased efforts in the future to maintain and improve it.

Read [CONTRIBUTING](CONTRIBUTING.md) to better understand what we're looking for. There's also a Developer Certificate of Origin that you'll need to sign off on.
​
## Notice

Copyright 2020 The MITRE Corporation

Approved for Public Release; Distribution Unlimited. Case Number 20-0325.
​
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

