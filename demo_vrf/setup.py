import importlib
import subprocess

required = ['serial', 'time', 'hmac', 'hashlib', 'argparse', 'pickle', 'dataclasses', 'os', 'collections']

missing = []
for package in required:
	try:
		importlib.import_module(package)
		print("Checked: "+package)
	except ImportError:
		missing.append(package)


if missing:
	print("Installing the following missing dependencies: ")
	for package in missing:
		print(package)

	subprocess.check_call(['pip3', 'install', *missing])


print("All dependencies verified or installed")