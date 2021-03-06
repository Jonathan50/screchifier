# Copyright (C) 2016 Jeandre Kruger
#
# This file is part of desnapifier.
#
# desnapifier is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# desnapifier is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with desnapifier.  If not, see <http://www.gnu.org/licenses/>.

import kurt
import notsupported, blocks

class NotEnoughArgumentsError(Exception):
    pass

class TooManyArgumentsError(Exception):
    pass

def check_args(s, c, n):
    if n < c:
        raise NotEnoughArgumentsError("not enough arguments for %s block" % s)
    if n > c:
        raise TooManyArgumentsError("too many arguments for %s block" % s)

def get_args(snap_block):
    args_list = []
    for child in snap_block:
        if child.tag == "l":
            args_list.append(child.text)
        if child.tag == "block":
            args_list.append(convert_block(child))
        if child.tag == "script":
            c_block_script = []
            for block in child:
                if block.tag == "block":
                    c_block_script += convert_block(block)
            args_list.append(c_block_script)
    return args_list

def get_variable(name):
    return kurt.Block("readVariable", name)

def convert_block(snap_block):
    scratch_blocks = None

    if not "s" in snap_block.attrib:
        if not "var" in snap_block.attrib:
            raise Exception("block has no s or var attribute!")
        scratch_blocks = [ get_variable(snap_block.attrib["var"]) ]
        return scratch_blocks

    s = snap_block.attrib["s"]

    # iterate over all possible blocks
    for key in blocks.blocks:
        if key == s:
            if blocks.blocks[key][0] != None:
                args = get_args(snap_block)
                check_args(s, blocks.blocks[key][1], len(args))
                scratch_blocks = [ kurt.Block(blocks.blocks[key][0], *args) ]
            else:
                if blocks.blocks[key][2] == None:
                    raise Exception("Both block[0] and block[2] are none!")
                scratch_blocks = blocks.blocks[key][2](snap_block)

    # unknown block
    if scratch_blocks == None:
        raise notsupported.UnsupportedBlockError(s)

    return scratch_blocks

def convert_scripts(snap_scripts):
    scratch_scripts = []

    for script in snap_scripts:
        if script.tag == "script":
            scratch_script = kurt.Script()
            for block in script:
               if block.tag == "block":
                  scratch_script.blocks += convert_block(block)
            scratch_scripts.append(scratch_script)

    return scratch_scripts
