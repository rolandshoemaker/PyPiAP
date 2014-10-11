import tarfile, ast, re, argparse
from zipfile import ZipFile
from os.path import isfile, join

def search_setup(text):
	try:
		text = text.decode('utf-8')
		text = re.sub('#+.*\n*', '', text) # kill python comments?
		install_match = re.search(r'install_requires=\[', text, re.MULTILINE+re.IGNORECASE)
		if install_match:
			startpos = endpos = install_match.end()
			if text[startpos] in [']']:
				return []
			in_quotes = False
			while True:
				if text[endpos] in ['"', '\'']:
					in_quotes = not in_quotes
				if text[endpos] == ']' and not in_quotes:
					break
				endpos += 1
			if endpos > startpos and [text[startpos], text[endpos]] in [['"', '"'], ['\'', '\'']]:
				install_line = re.sub('\s+|\n|#', '', install_line)
				return ast.literal_eval('['+install_line+']') or []
			else:
				return []
		else:
			return []
	except UnicodeDecodeError: # bailing since not sure how to handle atm
		return []

def extract_requirements(tarball, name):
    """Returns a list of requirements if requirements.txt exists in tarball."""
    if not tarball.split('.')[-1] == 'zip' and isfile(tarball):
        try:
            tar = tarfile.open(tarball)
        except tarfile.ReadError:
            return []
        try:
            r = tar.getmember(tar.getnames()[0]+'/requirements.txt')
            lines = tar.extractfile(r).readlines()
            return [line.decode('utf-8').rstrip('\n') for line in lines] or []
        except KeyError:
            # lets check setup.py then
            try:
                rr = tar.getmember(tar.getnames()[0]+'/'+name+'.egg-info/requires.txt')
                lines = tar.extractfile(rr).readlines()
                return [line.decode('utf-8').rstrip('\n') for line in lines] or []
            except KeyError:
                try:            
                    s = tar.getmember(tar.getnames()[0]+'/setup.py')
                    return search_setup(tar.extractfile(s).read())
                except KeyError:
                    return []
    elif tarball.split('.')[-1] == 'zip' and isfile(tarball): # it's a zip file not a tarball!
        with ZipFile(tarball, 'r') as zip:
            folder = ".".join(tarball.split('/')[-1].split('.')[:-1])
            try:
                r = zip.open(folder+'/requirements.txt')
                return [line.decode('utf-8').rstrip('\n') for line in r.readlines()] or []
            except KeyError:
                try:
                    rr = zip.open(folder+'/'+name+'.egg-info/requires.txt')
                    return [line.decode('utf-8').rstrip('\n') for line in rr.readlines()] or []
                except KeyError:
                    try:
                        s = zip.open(folder+'/setup.py')
                        return search_setup(s.read())
                    except KeyError:
                        return []
    return []