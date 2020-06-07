# Copyright 2020 NullConvergence
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


###
# This file assumes the project from the config file was already indexed
###
import argparse

from datetime import datetime
from graphrepo.miners import MineManager


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/pydriller.yml', type=str)
    return parser.parse_args()


def main():
    args = parse_args()

    if 'jax' in args.config:
        dev_query = {
            'hash': '93476add93abfb4fcfdd5c61ed811099bbb2aab70874f554d38bf381'}

    start = datetime.now()
    mine_manager = MineManager(config_path=args.config)
    method_updates = mine_manager.dev_miner.get_method_updates(
        dev_query['hash'],
        mine_manager.config.ct.project_id
    )
    complexity = [c['complexity']
                  for c in method_updates if c['complexity'] != -1]
    _ = sum(complexity) / len(complexity)

    print('Dev file types took {}'.format(datetime.now() - start))
    print('Nr method updates', len(method_updates))


if __name__ == '__main__':
    main()
