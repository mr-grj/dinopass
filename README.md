Stuff (Simple CLI Password Manager)
=======================

This repo exists to provide [an example setup.py] file, that can be used
to bootstrap your next Python project. It includes some advanced
patterns and best practices for `setup.py`, as well as some
commented–out nice–to–haves.

For example, this `setup.py` provides a `$ python setup.py upload`
command, which creates a *universal wheel* (and *sdist*) and uploads
your package to [PyPi] using [Twine], without the need for an annoying
`setup.cfg` file. It also creates/uploads a new git tag, automatically.

In short, `setup.py` files can be daunting to approach, when first
starting out — even Guido has been heard saying, "everyone cargo cults
thems". It's true — so, I want this repo to be the best place to
copy–paste from :)

[Check out the example!][an example setup.py]

Installation
-----

```bash
cd your_project

# Download the setup.py file:
#  download with wget
wget https://raw.githubusercontent.com/navdeep-G/setup.py/master/setup.py -O setup.py

#  download with curl
curl -O https://raw.githubusercontent.com/navdeep-G/setup.py/master/setup.py
```

Pull requests are encouraged!


License
-------

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any means.