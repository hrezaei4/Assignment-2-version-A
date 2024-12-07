#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py 
Author: "Hossein"
Semester: "Enter Winter/Summer/Fall Year"

The python code in this file is original work written by
"Student Name". No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: <Enter your documentation here>

'''

import argparse
import subprocess
import os, sys

def parse_command_args() -> object:
    "Set up argparse here. Call this function inside main."
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts",epilog="Copyright 2023")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    # add argument for "human-readable". USE -H, don't use -h! -h is reserved for --help which is created automatically.
    # check the docs for an argparse option to store this as a boolean.
    parser.add_argument("program", type=str, nargs='?', help="if a program is specified, show memory use of all associated processes. Show only total use is not.")
    args = parser.parse_args()
    return args
# create argparse function
# -H human readable
# -r running only

def percent_to_graph(percent: float, length: int=20) -> str:
    "turns a percent 0.0 - 1.0 into a bar graph"
    filled = int(percent * length)  
    empty = length - filled       
    return '#' * filled + ' ' * empty

def get_sys_mem() -> int:
    "return total system memory (used or available) in kB"
    with open("/proc/meminfo", "r") as f:
        for line in f:
            if line.startswith("MemTotal"):
                return int(line.split()[1])
            
def get_avail_mem() -> int:
    "return total memory that is available"
    with open("/proc/meminfo", "r") as f:
        for line in f:
            if line.startswith("MemAvailable"):
                 return int(line.split()[1])
            
def pids_of_prog(mimo: str) -> list:
    "given an app name, return all pids associated with app"
    try:
        result = subprocess.check_output(
            ["ps", "aux"], text=True
        )
        pids = []
        for line in result.splitlines():
            if mimo in line and not line.startswith("USER"):
                pid = int(line.split()[1])
                pids.append(pid)
        
        return pids
    
    except subprocess.CalledProcessError as e:
        print(f"Error executing ps command: {e}")
        return []
    
def rss_mem_of_pid(proc_id: str) -> int:
    "given a process id, return the resident memory used, zero if not found"
    try:
        with open(f"/proc/{proc_id}/status", "r") as f:
            for line in f:
                if line.startswith("VmRSS"):
                    return int(line.split()[1])
        return 0  
    except FileNotFoundError:
        return 0  
    
def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "turn 1,024 into 1 MiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB'] 
    suf_count = 0
    result = kibibytes
    while result > 1024 and suf_count < len(suffixes) - 1: 
        result /= 1024
        suf_count += 1
    return f'{result:.{decimal_places}f} {suffixes[suf_count]}'


def main():
    args = parse_command_args()

    if not args.program:
        total_mem = get_sys_mem() 
        available_mem = get_avail_mem()  
        used_mem = total_mem - available_mem  
        percent_used = used_mem / total_mem
        graph = percent_to_graph(percent_used)

        print(f"Total Memory: {bytes_to_human_r(total_mem)}")
        print(f"Used Memory: {bytes_to_human_r(used_mem)}")
        print(f"Available Memory: {bytes_to_human_r(available_mem)}")
        print(f"Memory Usage: {graph} ({percent_used * 100:.2f}%)")

    else:
        pids = pids_of_prog(args.program)  
        total_mem_used = 0

        for pid in pids:
            rss_mem = rss_mem_of_pid(pid)
            total_mem_used += rss_mem

        total_mem = get_sys_mem()  
        percent_used = total_mem_used / total_mem
        graph = percent_to_graph(percent_used)

        print(f"Total Memory: {bytes_to_human_r(total_mem)}")
        print(f"Used Memory by {args.program}: {bytes_to_human_r(total_mem_used)}")
        print(f"Memory Usage: {graph} ({percent_used * 100:.2f}%)")

if __name__ == "__main__":
    main()
