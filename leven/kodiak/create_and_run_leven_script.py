# be minded of the directory structure that must exists in kodiak for this to work:

# /data/pereza/ht/script_leven (.npy are stored here as <batch_start>_<batch_end>.npy)
# /data/pereza/ht/dataset.csv (data is read from here)
# /home/pereza/ht/leven_script.py
# /home/pereza/ht/create_and_run_leven_script.py (this script)
# /home/pereza/ht/script_leven (.sh are store here <batch_start>_<batch_end>.sh)

import sys, subprocess
path = '/home/pereza/ht/script_leven'
start = int(sys.argv[1])
end = int(sys.argv[2])
batch_size = int(sys.argv[3])
for i in range(start,end + 1,batch_size):
	sub_start = i
	sub_end = i+batch_size - 1
	if(sub_end > end):
		sub_end = end
	f = open(path + f'/{sub_start}_{sub_end}.sh', 'w')
	f.write(f"#!/bin/bash\n#PBS -l nodes=1:ppn=4\npip3 install leven\npython3 ht/leven_script.py {sub_start} {sub_end}")
	f.close()
	cmd = subprocess.Popen(['qsub','-l','nodes=1:ppn=4',path + f'/{sub_start}_{sub_end}.sh'])