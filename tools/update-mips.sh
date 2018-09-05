MIPS_URL=https://github.com/MIPSfpga/schoolMIPS.git
MIPS_PATH="."

git clone --single-branch $MIPS_URL $MIPS_PATH
rm -rf .git doc LICENSE program README.md scripts testbench .gitignore
tar -caf a.zip src/*
rm -rf src
# [dev] TODO complete script for updating School MIPS
