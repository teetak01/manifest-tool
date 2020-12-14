# ----------------------------------------------------------------------------
# Copyright 2019-2020 Pelion
#
# SPDX-License-Identifier: Apache-2.0
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
# ----------------------------------------------------------------------------

import argparse
import enum
import logging
import sys

from manifesttool import __version__
from manifesttool.mtool.actions.create import CreateAction
from manifesttool.mtool.actions.parse import ParseAction
from manifesttool.mtool.actions.public_key import PublicKeyAction
from manifesttool.mtool.actions.schema import PrintSchemaAction
from manifesttool.mtool.asn1.v1 import ManifestAsnCodecV1
from manifesttool.mtool.asn1.v3 import ManifestAsnCodecV3

logger = logging.getLogger('manifest-tool')


class Actions(enum.Enum):
    CREATE = 'create'
    CREATE_V1 = 'create-v1'
    PARSE = 'parse'
    SCHEMA = 'schema'
    PUB_KEY = 'public-key'


def get_parser():
    parser = argparse.ArgumentParser(
        description='Manifest tool for creating, signing and verifying '
                    'Pelion Device management update certificates'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='Manifest-Tool version {}'.format(__version__)

    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress information prints. Error prints only.'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Show exception info on error.'
    )

    actions_parser = parser.add_subparsers(dest='action')
    actions_parser.required = True
    create_parser = actions_parser.add_parser(
        Actions.CREATE.value,
        help='Create a Pelion Device management update certificate',
        add_help=False
    )
    CreateAction.register_parser_args(
        create_parser, ManifestAsnCodecV3.get_name())

    create_parser = actions_parser.add_parser(
        Actions.CREATE_V1.value,
        help='Create a Pelion Device management update certificate',
        add_help=False
    )
    CreateAction.register_parser_args(
        create_parser, ManifestAsnCodecV1.get_name())

    verify_parser = actions_parser.add_parser(
        Actions.PARSE.value,
        help='Parse and verify Pelion Device management update certificate',
        add_help=False
    )
    ParseAction.register_parser_args(verify_parser)

    schema_parser = actions_parser.add_parser(
        Actions.SCHEMA.value,
        help='Print input validation schema'
    )
    PrintSchemaAction.register_parser_args(schema_parser)

    schema_parser = actions_parser.add_parser(
        Actions.PUB_KEY.value,
        help='Get Uncompressed Public key in binary form'
    )
    PublicKeyAction.register_parser_args(schema_parser)

    return parser


def entry_point(argv=sys.argv[1:]):  # pylint: disable=dangerous-default-value
    parser = get_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s %(levelname)s %(message)s',
        level=logging.ERROR if args.quiet else logging.DEBUG
    )
    try:
        action = Actions(args.action)
        if action == Actions.PARSE:
            ParseAction.entry_point(args)
        elif action == Actions.CREATE:
            CreateAction.entry_point(args, ManifestAsnCodecV3)
        elif action == Actions.CREATE_V1:
            CreateAction.entry_point(args, ManifestAsnCodecV1)
        elif action == Actions.SCHEMA:
            PrintSchemaAction.entry_point(args)
        elif action == Actions.PUB_KEY:
            PublicKeyAction.entry_point(args)
        else:
            # will never get here
            raise AssertionError('Invalid action')
    except Exception as ex:  # pylint: disable=broad-except
        if args.debug:
            raise
        logger.error(
            str(ex),
            exc_info=args.debug
        )
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(entry_point())
