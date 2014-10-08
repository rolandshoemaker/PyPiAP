#!/usr/bin/python3
import tarfile

def extract_requirements(tarball):
	"""Returns a list of requirements if requirements.txt exists in tarball."""
	tar = tarfile.open(tarball)
	try:
		r = tar.getmember('requirements.txt')
		return [line.rstrip('\n') for line in tar.extractfile(r).readlines()]
	except KeyError:
		return []
