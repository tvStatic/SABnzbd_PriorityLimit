SABnzbd_PriorityLimit
=====================

Automatically set speed limit in SABnzbd based on priority of current job.

Monitors the SABnzbd server and changes the speed limit based on the priority of the
currently running job.

Configuration
=============

A documented example prioritylimit.ini file is provided. If an apikey is configured, 
the apikey entry must be uncommented and filled in.

Example configuration has a host of localhost:8080, a check interval of 30 seconds, and
priority limits set for low, normal, high and force of 50, 100, 400 and 0, respectively.
Log level is set to warnings/errors only.     

How to run
==========

This script uses the configobj module in sabnzbd.utils package. As a result, this script
should be run from the base directory of SABnzbd or PYTHONPATH should be set to include 
the base directory of SABnzbd.

To run: python prioritylimit.py

Process runs until killed.
