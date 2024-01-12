#!/bin/bash
echo -e "read_lef ./designs/ispd18.lef\nread_def $1\n" > run.tcl
openroad -gui run.tcl
