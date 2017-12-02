import json
import zipfile
import os
import zipfile
import gutenberg

records = None
def load_data(fh=None):
    global records
    if records is not None:
        return
    records = list()
    if fh is None:
        fh = open('47000_metadata.json')
    for line in fh:
        records.append(json.loads(line))

def search(fn):
    if records is None:
        load_data()
    return [rec for rec in records if fn(rec)]

def pluck(exprs, rec):
    results = list()
    for item in exprs:
        if hasattr(item, '__call__'):
            results.append(item(rec))
        else:
            results.append(rec[item])
    return results

def get_iso_text(gutenberg_id, iso_path="/Volumes/PGDVD_2010_04_RC2"):
    import re, glob
    sid = str(gutenberg_id)
    path = '/'.join([iso_path] + list(sid[:-1]) + [sid])
    for fname in glob.glob(path + "/*.ZIP"):
        zf = zipfile.ZipFile(fname, 'r')
        txtfiles = [f for f in zf.infolist() \
                if re.search(r'\.txt$', f.filename, re.I)]
        if len(txtfiles) > 0:
            return zf.read(txtfiles[0].filename).decode('latin1')
    raise ValueError("couldn't fetch " + sid) 

def get_tar_text(gutenberg_id, tar_path="/gutenberg/files"):
    import glob
    sid = str(gutenberg_id)
    path = '/'.join([tar_path] + list(sid[:-1]) + [sid])
    fnames = sorted(glob.glob(path + "/%s*.txt" % sid), reverse=True)
    try:
        return gutenberg.GutenbergCleaner(open(fnames[0], encoding='latin1').read()).extract_text()
    except (ValueError, IndexError):
        raise

if __name__ == '__main__':
    import pprint
    import re

    subjs = 'Fiction'
    books = [pluck(['gutenberg_id', 'title'], r) for r in \
                search(lambda x: any([re.search(subjs, t['identifier'], re.I)
                    for t in x['subjects']]))]
    print(len(books))
    pprint.pprint(books)
