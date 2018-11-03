#! /bin/bash

# if [ -f package.tar.xz ]; then
#     rm ./package.tar.xz
# fi

tar -hcJf package.tar.xz ../*.py ../stl ../python_utils /nfs-7/userdata/jguiang/chronosim/stl/*


