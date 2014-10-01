#!/bin/bash

set -o nounset
set -o errexit

export DYLD_LIBRARY_PATH=

source /Applications/Autodesk/maya2015/Maya.app/Contents/bin/MayaENV.sh

export MAYA_SCRIPT_PATH=$PWD

maya