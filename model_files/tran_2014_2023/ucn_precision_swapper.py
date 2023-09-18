import os
import sys
import shutil
sys.path.insert(0,"flopy")
import numpy as np
import flopy
print(flopy.__file__)


def swap_precision(org_filename,org_precision,new_filename,new_precision,echo=False):
	"""function to swap the precision of modflow .hds and mt3d(ms) .ucn files
	Args:
		org_filename (str): the original file
		new_filename (str): the new file to write
		org_precision (str): the precision of the original file. Must be
			"single" or "double"
		new_precision (str): the precision of the new file.  Must be
			"single" or "double"
	Note:
		This function relies on the org_filename extension to determine the file type
			(".hds" = head-save, ".ucn" = concentration)
		This function does not yet support modflow-6 gwt ucn files...easy to do tho
	Example:
		>>>org_filename = "MT3D0001.UCN"
		>>>new_filename = "single.ucn"
		>>>swap_precision(org_filename,new_filename,"double","single")
	"""

	assert os.path.exists(org_filename)
	assert org_filename != new_filename
	if os.path.exists(new_filename):
		os.remove(new_filename)
	org_precision = org_precision.strip().lower()
	new_precision = new_precision.strip().lower()
	if new_precision == org_precision:
		print("matching precision, just a copy...")
		shutil.copy2(org_filename,new_filename)
		return
	assert org_precision in ["single","double"],"unknown org_precision: '{0}'".format(org_precision)
	assert new_precision in ["single","double"],"unknown new_precision: '{0}'".format(new_precision)

	if org_filename.lower().endswith(".hds"):
		fxn = flopy.utils.HeadFile
	elif org_filename.lower().endswith(".ucn"):
		fxn = flopy.utils.UcnFile
	else:
		raise Exception("unrecognized org_filename '{0}' extension, must be '.hds' or '.ucn'".format(org_filename))
	if org_precision == "double":
		new_fmt = "<f4"
	else:
		new_fmt = "<f8"

	org_bfile = fxn(org_filename,precision=org_precision)
	org_header_dt = org_bfile.header_dtype
	new_header_items = [("totim",new_fmt) if d[0] == "totim" else d for d in org_header_dt.descr]
	new_header_items = [("pertim", new_fmt) if d[0] == "pertim" else d for d in new_header_items]
	header_dt = np.dtype(new_header_items)
	new_bfile = open(new_filename,'wb')
	for rec in org_bfile.recordarray:
		full_arr = org_bfile.get_data(totim=rec[3])
		if echo:
			print(rec,full_arr.dtype)
		full_arr = full_arr.astype(new_fmt)
		arr = full_arr[rec[-1]-1,:,:]
		header = np.array(tuple(rec), dtype=header_dt)
		header.tofile(new_bfile)
		arr.tofile(new_bfile)

	new_bfile.close()

org_filename = "MT3D001.UCN"
org_precision = "double"
new_filename = "MT3D001_single.UCN"
new_precision = "single"
swap_precision(org_filename,"double", new_filename, "single")