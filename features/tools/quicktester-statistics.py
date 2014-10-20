import sys
import os.path

from quicktester.plugin.statistic import quicktester_statistics


stat_path = os.path.join(os.getenv('QUICKTESTER_BEHAVE_PATH'), '.quicktester-statistics')
sys.argv[1:1] = ['-f', stat_path]

quicktester_statistics()
