#!/usr/bin/env python

import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-a","--add",nargs='+',help='add item')
parser.add_argument('-r','--remove', nargs = '+', type=int, help='remove item')
parser.add_argument('-p','--promote',nargs='+',type=int,help='promote item to top')
args = parser.parse_args()

def import_list(pth = 'list.txt'):
	return(open(pth).readlines())

def print_list():
	for n, item in enumerate(l):
		print("({}): {}".format(n+1, item))

def remove_item(to_remove):
	for n in reversed(to_remove):
		print("Removed: ", l.pop(n-1))

def add_items(items):
	for item in items:
		l.append(item + '\n')

def promote_items(items):
	for n in items:
		l.insert(0,l.pop(n-1))

def save_list(pth = 'list.txt'):
	with open(pth, 'w') as writer:
		writer.writelines(l)

def main():
	global l 
	l = import_list()

	if args.add:
		add_items(args.add)

	if args.remove:
		remove_item(args.remove)

	if args.promote:
		promote_items(args.promote)

	print("\n*****************")
	print("Nick's to-do list")
	print("*****************\n")
	print_list()
	save_list()

if __name__ == '__main__':
	main()