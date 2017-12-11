#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# This file is part of the NNGT project to generate and analyze
# neuronal networks and their activity.
# Copyright (C) 2015-2017  Tanguy Fardet
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Test functions for the NNGT """

import collections
try:
    from collections.abc import Container as _container
except:
    from collections import Container as _container

import numpy as np

import nngt


def valid_gen_arguments(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def on_master_process():
    '''
    Check whether the current code is executing on the master process (rank 0)
    if MPI is used.

    Returns
    -------
    True if rank is 0, if mpi4py is not present or if MPI is not used,
    otherwise False.
    '''
    try:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        if rank == 0:
            return True
        else:
            return False
    except ImportError:
        return True


def num_mpi_processes():
    ''' Returns the number of MPI processes (1 if MPI is not used) '''
    try:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        return comm.Get_size()
    except ImportError:
        return 1


def mpi_checker(func):
    '''
    Decorator used to check for mpi and make sure only rank zero is used
    to store and generate the graph if the mpi algorithms are activated.
    '''
    def wrapper(*args, **kwargs):
        if on_master_process():
            return func(*args, **kwargs)
        else:
            return None
    return wrapper


def mpi_random(func):
    '''
    Decorator asserting that all processes start with same random seed when
    using mpi.
    '''
    def wrapper(*args, **kwargs):
        try:
            from mpi4py import MPI
            comm = MPI.COMM_WORLD
            rank = comm.Get_rank()
            if rank == 0:
                state = np.random.get_state()
            else:
                state = None
            state = comm.bcast(state, root=0)
            np.random.set_state(state)
        except ImportError:
            pass
        return func(*args, **kwargs)
    return wrapper


def nonstring_container(obj):
    '''
    Returns true for any iterable which is not a string or byte sequence.
    '''
    if not isinstance(obj, _container):
        return False
    try:
        if isinstance(obj, unicode):
            return False
    except NameError:
        pass
    if isinstance(obj, bytes):
        return False
    if isinstance(obj, str):
        return False
    return True


def graph_tool_check(version_min):
    '''
    Raise an error for function not working with old versions of graph-tool.
    '''
    old_graph_tool = _old_graph_tool(version_min)

    def decorator(func):
        def wrapper(*args, **kwargs):
            if old_graph_tool:
                raise NotImplementedError('This function is not working for '
                                          'graph-tool < ' + version_min + '.')
            else:
                return func(*args, **kwargs)
        return wrapper

    return decorator


def _old_graph_tool(version_min):
    '''
    Check for old versions of graph-tool for which some functions are not
    working.
    '''
    return (nngt.get_config('graph_library') == 'graph-tool'
            and nngt.get_config('library').__version__[:4] < version_min)
