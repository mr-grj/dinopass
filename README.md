DinoPass 
=======================

```
               __
              / _) -- I'm DinoPass and I can help you administer
     _.----._/ /          your passwords directly from CLI!
    /         /
 __/ (  | (  |
/__.-'|_|--|_|
```

## Description

DinoPass was first created to satisfy my own needs. Because I tend to change my 
passwords pretty frequently I usually find myself in a position of having to reset 
them kinda often. So there's that. 


## How it works and what it does

Everything is meant to be as easy and intuitive as possible. You're going to be asked
for a master password which is going to be the only one that you'll need to remember
(so please make sure it's gonna be as strong as possible!). After you'll enter your
master password these are all the options that are currently available:

* List all your passwords  (WARNING: It's going to be in clear text!)
* Purge all your passwords (WARNING: This is permanent so do it at your own risk!)
* Create a new password
* Update an existing password
* Retrieve an existing password (by name)
* Delete an existing password


## Installation

Installing DinoPass is as simple as:

```shell script
python3.8 setup.py install
```

## Usage

You can always check the help menu by running:

```shell script
dinopass --help

Usage: cli.py [OPTIONS] COMMAND [ARGS]...

  DinoPass - Simple CLI Password manager

Options:
  --help  Show this message and exit.

Commands:
  all     List all credentials.
  create  Create a new credential with a specific name and password.
  delete  Delete a specific credential by name.
  get     Get a specific credential by name.
  purge   Purge all credentials.
  update  Update a credential field matching a specific condition with a
          new value


All the arguments are mutually exclusive
```

## TO DO

* Add type annotations
* Add tests
* Improve readme (add installation process, how the passwords are stored, etc)


License
-------

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any means.