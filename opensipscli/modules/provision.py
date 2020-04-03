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
from opensipscli import comm

import os
from xml.etree import ElementTree
from collections import OrderedDict

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
        helper method for autocompletion in interactive mode
        """
        modules = comm.execute('pi_list')
        dbs = [key for key, value in modules.items()]
        if len(line.split()) < 3:
            if not text:
                return dbs
            ret = [d for d in dbs if d.startswith(text)]
        else:
            if len(line.split()) == 3:
                if line.split()[2] not in dbs:
                    if not text:
                        return dbs
                    ret = [d for d in dbs if d.startswith(text)]
                else:
                    tables = self.get_tables(dbs)
                    db = line.split()[2]
                    if not text:
                        return tables[db]
                    ret = [t for t in tables[db] if t.startswith(text)]
            else:
                tables = self.get_tables(dbs)
                db = line.split()[2]
                if len(line.split()) == 4:
                    if line.split()[3] not in tables[db]:
                        if not text:
                            return tables[db]
                        ret = [t for t in tables[db] if t.startswith(text)]
                    else:
                        table = line.split()[3]
                        columns = self.get_columns(table, command)
                        if command != 'show':
                            columns = [c + '=' for c in columns]
                        if not text:
                            return columns
                        ret = [c for c in columns if c.startswith(text)]
                else:
                    table = line.split()[3]
                    columns = self.get_columns(table,command)
                    if command != 'show':
                        columns = [c + '=' for c in columns]
                    if not text:
                        return columns
                    ret = [c for c in columns if c.startswith(text)]
        if len(ret) == 1 and ret[0][-1] != '=':
            ret[0] = ret[0] + ' '
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

    def get_tables(self, db_list):
        """
        method that retrieves available tables
        """
        fpath = os.path.join(DEFAULT_DB_PATH, 'pi_framework.xml')
        tree = ElementTree.parse(fpath)
        table_dict = {i: [] for i in db_list}
        tables = tree.findall('mod/mod_name')
        for db in table_dict.keys():
            path = os.path.join(DEFAULT_DB_PATH, db + '-mod')
            for table in tables:
                with open(path) as f:
                    if table.text in f.read():
                        table_dict[db].append(table.text)
        return table_dict

    def get_columns(self, table_name, cmd):
        """
        method that retireves available columns in a table
        """
        fpath = os.path.join(DEFAULT_DB_PATH, 'pi_framework.xml')
        tree = ElementTree.parse(fpath)
        dbs = tree.findall('mod')
        table_cols = []
        for db in dbs:
            table = db.find('mod_name')
            if table.text == table_name:
                commands = db.findall('cmd')
                for command in commands:
                    cmd_name = command.find('cmd_name')
                    if cmd_name.text == cmd:
                        if cmd == 'update' or cmd == 'delete':
                            ccols = command.findall('clause_cols/col/field')
                            if cmd == 'update':
                                for ccol in ccols:
                                    table_cols.append('update.' + ccol.text)
                            else:
                                for ccol in ccols:
                                    table_cols.append('delete.' + ccol.text)
                        cols = command.findall('query_cols/col/field')
                        for col in cols:
                            table_cols.append(col.text)
        return table_cols

    def do_show(self, params=None):
        """
        method that implements the show command
        """
        command_obj = OrderedDict()
        command_obj["command"] = "show"
        command_obj["module"] = ""
        command_obj["table"] = ""
        command_obj["values"] = []
        if len(params) < 1:
            db_name = cfg.read_param(None,
                      "Please provide the database you want to display from")
            if not db_name:
                logger.warning("no database to show!")
                return -1
        else:
           db_name = params[0]
        command_obj["module"] = db_name

        if len(params) < 2:
            table_name = cfg.read_param(None,
                         "Please provide the table you want to display from")
            if not table_name:
                logger.warning("no table to show!")
                return -1
        else:
            table_name = params[1]
        command_obj["table"] = table_name

        if len(params) < 3:
            col_names = cfg.read_param(None,
                       "Please provide at least a column to display from")
            if not col_names:
                logger.warning("no column to show!")
                return -1
        else:
            col_names = params[2:]
        command_obj["values"] = [c for c in col_names]
        
        return command_obj

    def do_add(self, params=None):
        """
        method that implements add command
        """
        command_obj = OrderedDict()
        command_obj["command"] = "add"
        command_obj["module"] = ""
        command_obj["table"] = ""
        command_obj["values"] = OrderedDict()
        if len(params) < 1:
            db_name = cfg.read_param(None,
                      "Please provide the database you want to add to")
            if not db_name:
                logger.warning("no database to add!")
                return -1
        else:
            db_name = params[0]
        command_obj["module"] = db_name

        if len(params) < 2:
            table_name = cfg.read_param(None,
                         "Please provide the table you want to add to")
            if not table_name:
                logger.warning("no table to add!")
                return -1
        else:
            table_name = params[1]
        command_obj["table"] = table_name

        if len(params) < 3:
            col_names = cfg.read_param(None,
                       "Please provide at least a column you want to add to
                                                                (<column>=<>)")
            if not col_names:
                logger.warning("no column to add!")
                return -1
        else:
            col_names = params[2:]
        for col in col_names:
            command_obj["values"][col.split('=')[0]] = col.split('=')[1]
        
        return command_obj

    def do_update(self, params=None):
        """
        method that implements update command
        """
        command_obj = OrderedDict()
        command_obj["command"] = "update"
        command_obj["module"] = ""
        command_obj["table"] = ""
        command_obj["update.id"] = ""
        command_obj["values"] = OrderedDict()
        if len(params) < 1:
            db_name = cfg.read_param(None,
                      "Please provide the database you want to update")
            if not db_name:
                logger.warning("no database to update!")
                return -1
        else:
            db_name = params[0]
        command_obj["module"] = db_name

        if len(params) < 2:
            table_name = cfg.read_param(None,
                         "Please provide the table you want to update")
            if not table_name:
                logger.warning("no table to update!")
                return -1
        else:
            table_name = params[1]
        command_obj["table"] = table_name

        if len(params) < 3:
            update_id = cfg.read_param(None,
                       "Please provide the id you want to update(update.id=<>)")
            if not update_id:
                logger.warning("no id to update")
                return -1
        else:
            update_id = params[2]
        command_obj["update.id"] = update_id.split('=')[1]

        if len(params) < 4:
            col_names = cfg.read_param(None,
                        "Please provide at least a column you want to update
                                                                (<column>=<>)")
            if not col_names:
                logger.warning("no column to update!")
                return -1
        else:
            col_names = params[3:]
        for col in col_names:
            command_obj["values"][col.split('=')[0]] = col.split('=')[1]
        
        return command_obj

    def do_delete(self, params=None):
        """
        method that implements delete command
        """        
        command_obj = OrderedDict()
        command_obj["command"] = "delete"
        command_obj["module"] = ""
        command_obj["table"] = ""
        command_obj["delete.id"] = ""
        if len(params) < 1:
            db_name = cfg.read_param(None,
                      "Please provide the database you want to delete from")
            if not db_name:
                logger.warning("no database to delete!")
                return -1
        else:
            db_name = params[0]
        command_obj["module"] = db_name

        if len(params) < 2:
            table_name = cfg.read_param(None,
                         "Please provide the table you want to delete from")
            if not table_name:
                logger.warning("no table to delete!")
                return -1
        else:
            table_name = params[1]
        command_obj["table"] = table_name

        if len(params) < 3:
            delete_id = cfg.read_param(None,
                       "Please provide the id you want to delete(update.id=<>)")
            if not delete_id:
                logger.warning("no id to delete!")
                return -1
        else:
            delete_id = params[2]
        command_obj["delete.id"] = delete_id.split('=')[1]
        
        return command_obj

