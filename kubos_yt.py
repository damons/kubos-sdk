#!/usr/bin/env python

import argparse
import os
import subprocess
import sys
import urllib2
import xml.etree.ElementTree as ET

yotta_cmd = 'yotta'
install_cmd = 'install'
target_cmd  = 'target'

kubos_rt = 'kubos-rt'
org_name = 'openkosmosorg'
branch = 'master'
target_prefix = 'target-'   #prefix on every target repo name
kubos_rt_full_path = '%s@%s/%s#%s' % (kubos_rt, org_name, kubos_rt, branch)

KubOS_manifest_url = 'https://raw.githubusercontent.com/openkosmosorg/kubos-manifest/master/default.xml'

def main():
    parser = argparse.ArgumentParser(description = 'Kubos wrapper for yotta')
    parser.add_argument('--init', action='store_true', default=False, help='Create a new module')
    parser.add_argument('--target', nargs='?', type=str, help='Set target device')
    args, anonymous_args = parser.parse_known_args()

    if args.init:
        cmd(yotta_cmd, 'init')
        set_target(None)    #Avoid using the default yotta_cmd target which requires Mbed login
        install_dependencies()
    elif args.target:
        set_target(args.target)
    elif len(anonymous_args) > 0:
        cmd (yotta_cmd, ' '.join(anonymous_args))


def cmd(*args, **kwargs):
    # print ' '.join(args)
    try:
        subprocess.check_call(args, **kwargs)
    except subprocess.CalledProcessError, e:
        print >>sys.stderr, 'Error executing command, giving up'
        sys.exit(1)


def set_target(target):
    target_list = parse_targets()
    display_list = drop_prefix(target_list)   
    
    if target == None: # set the default target to the first target in the manifest file
        target = display_list[0]

    if target not in display_list:
        print >>sys.stderr, 'Error: "%s" is not an available KubOS target.' % target
        print >>sys.stderr, 'Available targets are: %s' % (', '.join(display_list))
        sys.exit(1)
        
    target_path = ''.join([target, '@', org_name, '/', target_prefix, target, '#', branch])
    cmd(yotta_cmd, target_cmd, target_path)


def install_dependencies():
    cmd(yotta_cmd, install_cmd, kubos_rt_full_path)


def parse_targets():
    targets = []
    connection = urllib2.urlopen(KubOS_manifest_url) #get and parse the targets from the KubOS repo manifest
    manifest = connection.read()
    root = ET.fromstring(manifest)
    for child in root:
        child_name = str(child.attrib.get('name'))
        if child_name.find('target') != -1:    #parse out targets by repo name
            targets.append(child_name)
    return targets


def drop_prefix(input_list): # Removes prefix string 'target-' from input list
    output_list = []
    for item in input_list:
        if (item.startswith(target_prefix)):  
            output_list.append(item[7:])
    return output_list


if __name__ == '__main__':
    main()
           
