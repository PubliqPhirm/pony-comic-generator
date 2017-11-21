from shutil import copyfile
import os
import subprocess
from subprocess import DEVNULL, STDOUT, check_call
import compareImages
os.rename('../config.cfg','../config_orig.cfg')
copyfile('testconfig.cfg','../config.cfg')

similar=0
for fn in os.listdir('testLogs'):
	print(fn)
	p = subprocess.Popen(["python3", "generateComic.py", '-f',"testSystem/testLogs/"+fn, '-b',"backgrounds/IRL/020409182610-vibes.jpg"], cwd='..', stdout=DEVNULL, stderr=STDOUT)
	p.wait(69)
	copyfile('../comic.jpg', 'testResults/'+fn+'.jpg')
	difference = compareImages.compareImages('testResults/'+fn+'.jpg', 'defaultResults/'+fn+'.jpg')
	print('  image is ' + "{0:.2f}".format(difference) + '% different than the default')
	if difference<3:
		print('  TEST PASS')
		similar+=1
	else:
		print('  TEST FAIL')

print(str(similar)+'/'+str(len(os.listdir('testLogs')))+' tests successful')

os.remove('../config.cfg')
os.rename('../config_orig.cfg','../config.cfg')
