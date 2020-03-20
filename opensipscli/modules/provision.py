#!/usr/bin/env python
##
## This file is part of OpenSIPS CLI
## (see https://github.com/OpenSIPS/opensips-cli).
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <http://www.gnu.org/licenses/>.
##

from opensipscli.module import Module
from opensipscli.logger import logger
from opensipscli.config import cfg
from opensipscli.db import (
        osdb, osdbError
)

import os
from xml.etree import ElementTree

DEFAULT_DB_PATH = "/usr/share/opensips/pi_http"

class provision(Module):
    """
    Class: provisioning modules
    """
    def __init__(self):
        """
        Constructor
        """
        pass

    def __complete__(self, command, text, line, begidx, endidx):
        """
        autocompletion method in interactive mode
        """
        dbs = self.get_tables()
        if len(line.split()) < 3:
            if not text:
                return list(dbs.keys())
            ret = [d for d in dbs.keys() if d.startswith(text)]
        else:
            if len(line.split()) == 3:
                if line.split()[2] not in dbs.keys():
                    if not text:
                        return list(dbs.keys())

                    ret = [d for d in dbs.keys() if d.startswith(text)]
                else:
                    if not text:
                        return dbs[line.split()[2]]
                    ret = [t for t in dbs[line.split()[2]] if t.startswith(text)]
            else:
                if not text:
                    return dbs[line.split()[2]]
                ret = [t for t in dbs[line.split()[2]] if t.startswith(text)]
        return ret or ['']

    def __get_methods__(self):
        """
        methods available for autocompletion
        """
        return [
            'show',
            'add',
            'update',
            'delete',
            ]

    def get_files(self):
        """
        method that retrieves available dbs
        """
        db_list = os.listdir(DEFAULT_DB_PATH)
        db_list = [db_list[i].split('-')[0] for i in range(len(db_list))]
        db_list = [db for db in db_list if not db.startswith('pi')]
        db_list = list(dict.fromkeys(db_list))
        db_list = sorted(db_list)
        return db_list

    def get_tables(self):
        """
        method that retrieves available tables
        """
        fpath = os.path.join(DEFAULT_DB_PATH, "pi_framework.xml")
        tree = ElementTree.parse(fpath)
        table_dict = {i: [] for i in self.get_files()}
        tables = tree.findall('mod/mod_name')
        for db in table_dict.keys():
            path = os.path.join(DEFAULT_DB_PATH, db + "-mod")
            for table in tables:
                with open(path) as f:
                    if table.text in f.read():
                        table_dict[db].append(table.text)
        return table_dict

    def do_show(self, params=None):
        
        if len(params) < 1:
            db_name = cfg.read_param(None,
                      "Please provide the database you want to display from")
            if not db_name:
                logger.warning("no database to show!")
                return -1
        else:
           db_name = params[0]

        if len(params) < 2:
            table_name = cfg.read_param(None,
                         "Please provide the table you want to display from")
            if not table_name:
                logger.warning("no table to show!")
                return -1
        else:
            table_name = params[1]

        if len(params) < 3:
            col_name = cfg.read_param(None,
                       "Please provide the column you want to display from")
            if not col_name:
                logger.warning("no column to show!")
                return -1
        else:
            col_name = params[2]

    def do_add(self, params=None):

        if len(params) < 1:
            db_name = cfg.read_param(None,
                      "Please provide the database you want to add to")
            if not db_name:
                logger.warning("no database to add!")
                return -1
        else:
            db_name = params[0]

        if len(params) < 2:
            table_name = cfg.read_param(None,
                         "Please provide the table you want to add to")
            if not table_name:
                logger.warning("no table to add!")
                return -1
        else:
            table_name = params[1]

        if len(params) < 3:
            col_name = cfg.read_param(None,
                       "Please provide the column you want to add to")
            if not col_name:
                logger.warning("no column to add!")
                return -1
        else:
            col_name = params[2]

        if len(params) < 4:
            cmd_input = cfg.read_param(None,
                        "Please provide an input for your command")
            if not cmd_input:
                logger.warning("no input given!")
                return -1
        else:
            cmd_input = params[3]

    def do_update(self, params=None):

        if len(params) < 1:
            db_name = cfg.read_param(None,
                      "Please provide the database you want to update")
            if not db_name:
                logger.warning("no database to update!")
                return -1
        else:
            db_name = params[0]

        if len(params) < 2:
            table_name = cfg.read_param(None,
                         "Please provide the table you want to update")
            if not table_name:
                logger.warning("no table to update!")
                return -1
        else:
            table_name = params[1]

        if len(params) < 3:
            col_name = cfg.read_param(None,
                       "Please provide the column you want to update")
            if not col_name:
                logger.warning("no column to update")
                return -1
        else:
            col_name = params[2]

        if len(params) < 4:
            cmd_input = cfg.read_param(None,
                        "Please provide an input for your command")
            if not cmd_input:
                logger.warning("no input given!")
                return -1
        else:
            cmd_input = params[3]

    def do_delete(self, params=None):

        if len(params) < 1:
            db_name = cfg.read_param(None,
                      "Please provide the database you want to delete from")
            if not db_name:
                logger.warning("no database to delete!")
                return -1
        else:
            db_name = params[0]

        if len(params) < 2:
            table_name = cfg.read_param(None,
                         "Please provide the table you want to delete from")
            if not table_name:
                logger.warning("no table to delete!")
                return -1
        else:
            table_name = params[1]

        if len(params) < 3:
            col_name = cfg.read_param(None,
                       "Please provide the column you want to delete from")
            if not col_name:
                logger.warning("no column to delete!")
                return -1
        else:
            col_name = params[2]

