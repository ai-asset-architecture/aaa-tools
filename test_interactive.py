import pexpect
import sys
import shutil

# Make sure aaa tool is available or run via python -m
cmd = f"{sys.executable} -m aaa.cli init interactive --output-dir test_policy"

child = pexpect.spawn(cmd, encoding='utf-8')
child.logfile = sys.stdout

child.expect("Policy Name")
child.sendline("test-policy")

child.expect("Version")
child.sendline("0.1.0")

child.expect("Add a rule?")
child.sendline("y")

child.expect("Rule ID")
child.sendline("check_readme")

child.expect("Description")
child.sendline("Ensure README exists")

child.expect("Check Type")
child.sendline("file_exists")

child.expect("File Path")
child.sendline("README.md")

child.expect("Severity")
child.sendline("blocking")

child.expect("Add a rule?")
child.sendline("n")

child.expect("Compile to Python script now?")
child.sendline("y")

child.expect(pexpect.EOF)
print("\nInteractive test done.")
