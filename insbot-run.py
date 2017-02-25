# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.join(sys.path[0],'src'))

from insbot import InsBot
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--username', '-u', type=str, required=True, help='Your instagram username')
parser.add_argument('--password', '-pw', type=str, required=True, help='Your instagram password')
parser.add_argument('--likes', '-l', type=int, required=True, help='Maximum likes per day')
parser.add_argument('--follows', '-f', type=int, required=True, help='Maximum follows per day')
parser.add_argument('--unfollows', '-un', type=int, required=True, help='Maximum unfollows per day')
parser.add_argument('--token', '-t', type=str, required=True, help='Access token for instagram API, Get it from sniffing ink361 traffic.')
parser.add_argument('--maxlikesfortag', '-mlft', type=int, required=False, default=50, help='Maximum likes per tag')
parser.add_argument('--logtofile', '-log', required=False, help='Add this in order to log to a file', action='store_true')
parser.add_argument('--clear', '-c', required=False, help='Clear screen after each iteration', action='store_true')

bot_args = parser.parse_args()

#########################
## Example command line:
## insbot-run.py -u USERNAME -pw PASSWORD -l 1000 -f 500 -un 800 -t 0000000000.0000000.00000000000000000000000000000000 -c -log
#########################

bot = InsBot(login=bot_args.username, password=bot_args.password,
               like_per_day=bot_args.likes,
               comments_per_day=0,
               tag_list=['nature', 'view', 'earth', 'planet', 'f4f', 'follow4follow'],
               max_like_for_one_tag=bot_args.maxlikesfortag,
               follow_per_day=bot_args.follows,
               unfollow_per_day=bot_args.unfollows,
               unfollow_break_min=15,
               unfollow_break_max=30,
               log_to_file=bot_args.logtofile,
               clear_after_iter=bot_args.clear,
               token=bot_args.token,
               unwanted_username_list=['free','likes'])


bot_mode_input = 0
def main():
	while True:
	  if bot_mode_input == 0 :
	    bot.run_bot_run()
	  else:
	    print 'Mode %i does not exist.' % bot_mode_input


if __name__ == '__main__':
	main()
