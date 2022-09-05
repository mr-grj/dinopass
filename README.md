DinoPass - your personal password manager!
=======================

```
               __
              / _) -- I'm DinoPass and I can help you administer
     _.----._/ /          your passwords in a dino-easy way!
    /         /
 __/ (  | (  |
/__.-'|_|--|_|
```

## Description

DinoPass was created to satisfy my own needs. Because I tend to change my
passwords pretty frequently I usually find myself in a position of having to reset
them kinda often. So there's that.


## How it works and what it does

Everything is meant to be as easy and intuitive as possible. You're going to be asked
for a master password which is going to be the only one that you'll need to remember
(so please make sure it's going to be as complex as possible!). After you'll enter your
master password these are all the options that are currently available:

* List all your passwords  (WARNING: It's going to be in clear text!)
* Purge all your passwords (WARNING: This is permanent so do it at your own risk!)
* Create a new password
* Update an existing password
* Retrieve an existing password (by name)
* Delete an existing password

## Technical details

This tool uses the following technologies:

* Python >= 3.10 + FastAPI + SQLAlchemy
* Poetry
* PostgreSQL
* React + JS
* Docker & docker-compose

I've decided that I want this service to be powered by an API backend, so that I can
easily extend it. The interface was created out of boredom so don't expect it to be
too professional.

### Workflow

There are (currently) only two tables stored in our DB: `master_password` and
`password`. The former stores the main / master password, which is encrypted
using SHA-512 algorithm. The latest, is going to store all of your passwords,
which get encrypted using your master password's hash.

## Usage

Because I wanted to make things as easy as they can get, I've used `docker` and
`docker-compose` for almost everything. So, to get this up & running you have to:

```shell
docker-compose up --build
```

License
-------

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any means.
