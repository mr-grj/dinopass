Stuff (Simple CLI Password Manager)
=======================

Stuff is a Python library for managing your own passwords in a CLI-based manner.


## Description

This library was first created to satisfy my own needs of handling my passwords. Because
I tend to change my passwords pretty frequently I usually find myself in a position of 
having to reset them kinda often.


## Usage

```shell script
Usage: stuff.py [-h] (-a | -p | -c <name> <group> <password> | -g <field> <value> | -u <field> <value> <field_to_update> <new_value> | -d <field> <value>)

Simple CLI Password manager for personal use

Optional arguments:
  -h, --help            show this help message and exit

  -a, --all             List all credentials
  -p, --purge           Purge all credentials

  -c <name> <group> <password>, --create <name> <group> <password>
                        Create a new credential with a specific name, in a specific group, with a specific password
  -g <field> <value>, --get <field> <value>
                        Get a specific credential by name/group value
  -u <field> <value> <field_to_update> <new_value>, --update <field> <value> <field_to_update> <new_value>
                        Update a credential field matching a specific condition with a new value
  -d <field> <value>, --delete <field> <value>
                        Delete a specific credential by name/group value

All the arguments are mutually exclusive

```

**Pull requests are encouraged!**

License
-------

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any means.