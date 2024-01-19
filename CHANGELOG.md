# CHANGELOG



## v1.0.4 (2023-08-02)

### Documentation

* docs(LICENSE.md): Added license

Added LICENSE.md file ([`9f99127`](https://github.com/mibs510/OpenALPR-Webhook/commit/9f991272ccb1aa79a39b05538c2224d1ca7f5959))

### Fix

* fix(cache_service &amp; cache): out of index &amp; constructor

Fixed condition to prevent out of index error in get_second_top_region_*
methods
Fixed constructor in cache model to update time, year, and
month.

Signed-off-by: Connor &lt;connor@mcmillan.website&gt; ([`6876464`](https://github.com/mibs510/OpenALPR-Webhook/commit/6876464dce6d19e9a574aef3bb85217bccd04467))

### Unknown

* Merge remote-tracking branch &#39;origin/master&#39; ([`9263625`](https://github.com/mibs510/OpenALPR-Webhook/commit/9263625942de957a74d4f1a83f687635456d497b))

* Merge remote-tracking branch &#39;origin/master&#39; ([`cc8303c`](https://github.com/mibs510/OpenALPR-Webhook/commit/cc8303cabacc6485e22d71e55de0e3b4dc02d6fd))


## v1.0.3 (2023-07-13)

### Chore

* chore(branding): New logo

Rebranded OpenALPR-Webhook logo, favicons, etc

Signed-off-by: Connor &lt;connor@mcmillan.website&gt; ([`e588cae`](https://github.com/mibs510/OpenALPR-Webhook/commit/e588caeda5033ffeb5eba0f9a5dde2ba0f9788fe))

### Fix

* fix(sidebar.html): img src

Updated src attribute of img tag. ([`1792473`](https://github.com/mibs510/OpenALPR-Webhook/commit/1792473a4888acf05bfabf4ff9d2c2543b365dc7))

### Unknown

* Merge remote-tracking branch &#39;origin/master&#39; ([`3b475f0`](https://github.com/mibs510/OpenALPR-Webhook/commit/3b475f0544c52ce11aa5b0991045b8b86b5dd0de))


## v1.0.2 (2023-07-12)

### Fix

* fix(README.md + cache_service): Update last_seen

Added missing last_seen update to datetime.utcnow() for each agent and
camera. Last seen column was not updating.
Fixed some formatting in
README.md ([`4263822`](https://github.com/mibs510/OpenALPR-Webhook/commit/4263822380a946d8cdf32ec6fbf4509dcad8e7c9))

### Unknown

* Merge remote-tracking branch &#39;origin/master&#39; ([`1ddf8de`](https://github.com/mibs510/OpenALPR-Webhook/commit/1ddf8de2ae4107e18176426c68431e579577a4af))


## v1.0.1 (2023-07-12)

### Fix

* fix(setup.py + index.html): packages &amp; url_for()

Fixed error: package directory &#39;apps/alpr/ipban&#39; does not
exist
by
removing said directory from packages in setup.py
Fixed
url_for() in
See all under Custom alerts in index.html ([`2067c1c`](https://github.com/mibs510/OpenALPR-Webhook/commit/2067c1cc021bcc2cc42f467b67df8d1d606d32a6))


## v1.0.0 (2023-07-12)

### Breaking

* fix(a lot): Copyright + Unqlite

Added copyright to appicable files and removed unqlite code which is
no
longer needed.
Updated Upcoming features &amp; Updates section in
README.md

BREAKING CHANGE: Does not break anything... maybe the ability to import
unqlite databases.
Using this break to bump the major as a means of
officially releasing v1 ([`d548a4a`](https://github.com/mibs510/OpenALPR-Webhook/commit/d548a4a8a4efc98dfaecb61f5c17f2aefbc587eb))

### Unknown

* Merge remote-tracking branch &#39;origin/master&#39;

# Conflicts:
#	version.py ([`bd8ea00`](https://github.com/mibs510/OpenALPR-Webhook/commit/bd8ea00bee6a49108c7e45ae6c6b734716bd96f9))


## v0.0.10 (2023-07-10)

### Fix

* fix(ipban_config.py): Changed logdir

Changed logdir to point to logs/ipban/ ([`3b0af32`](https://github.com/mibs510/OpenALPR-Webhook/commit/3b0af323c5dba87ce1873527217d59114b089cb7))


## v0.0.9 (2023-07-09)

### Fix

* fix(setup.py): packages

Fixed error: package directory &#39;apps/uploads&#39; does not exist ([`323b947`](https://github.com/mibs510/OpenALPR-Webhook/commit/323b9477a67692c10c8aeffdb18285a2b7be936f))

### Unknown

* Merge remote-tracking branch &#39;origin/master&#39; ([`1eb4787`](https://github.com/mibs510/OpenALPR-Webhook/commit/1eb4787b037474341bc8749cb27776754787a220))


## v0.0.8 (2023-07-09)

### Fix

* fix(setup.py): packages

Fixed error: error: package directory &#39;apps/downloads&#39; does not exist ([`faf2f1c`](https://github.com/mibs510/OpenALPR-Webhook/commit/faf2f1c33841eef6f968da672f45ca7c7bba7ef7))

### Unknown

* Merge remote-tracking branch &#39;origin/master&#39; ([`b5442e0`](https://github.com/mibs510/OpenALPR-Webhook/commit/b5442e0fb054f7ddc1950857243274d039d140b9))


## v0.0.7 (2023-07-09)

### Fix

* fix(setup.py): packages

Fixed error: package directory &#39;apps/alpr/routes/settings/vehicle&#39; does
not exist ([`34cbefc`](https://github.com/mibs510/OpenALPR-Webhook/commit/34cbefcbe0d49767bd85271aed37c5134bd82494))

### Unknown

* Merge remote-tracking branch &#39;origin/master&#39; ([`ae5fba2`](https://github.com/mibs510/OpenALPR-Webhook/commit/ae5fba24465357b0213eb6ccd051f7686d57bbdb))


## v0.0.6 (2023-07-09)

### Fix

* fix(__init__.py): subprocess.Popen()

Defined venv/bin/python3 absolute path for Worker Manager Server. ([`11c4277`](https://github.com/mibs510/OpenALPR-Webhook/commit/11c4277bf324f8b603157d4524a781fa1502882b))

### Unknown

* Merge remote-tracking branch &#39;origin/master&#39; ([`94a0c24`](https://github.com/mibs510/OpenALPR-Webhook/commit/94a0c24cef281fd2639ecb3ed91929640e58128c))


## v0.0.5 (2023-07-08)

### Fix

* fix(README.md): Installation

Some minor fixes to aid README.md for installation section. ([`ae41cd4`](https://github.com/mibs510/OpenALPR-Webhook/commit/ae41cd4593f0786f574c886aa54fdebbc40f5690))

### Unknown

* Merge remote-tracking branch &#39;origin/master&#39; ([`50c1ae9`](https://github.com/mibs510/OpenALPR-Webhook/commit/50c1ae9fcac06bce6afaf43c45d75d3258b79c88))


## v0.0.4 (2023-07-08)

### Fix

* fix(requirements.txt): Synced packages

Performed a pip freeze and updated requirements.txt ([`2d47f3b`](https://github.com/mibs510/OpenALPR-Webhook/commit/2d47f3b0ca385dc3cd503681d81a9eab85ee3d02))

### Unknown

* Merge remote-tracking branch &#39;origin/master&#39; ([`cd779d4`](https://github.com/mibs510/OpenALPR-Webhook/commit/cd779d481ad079ef6a4bd1ba3f919050c53f90c9))


## v0.0.3 (2023-07-08)

### Fix

* fix(apps): setup.py

Added packages to setup.py ([`0ac2d6f`](https://github.com/mibs510/OpenALPR-Webhook/commit/0ac2d6fa7a29eebc3573769ca8d9218e4c80fbae))

### Unknown

* Merge remote-tracking branch &#39;origin/master&#39; ([`241bfa2`](https://github.com/mibs510/OpenALPR-Webhook/commit/241bfa249e239d1633e58c869ddceff9a6645c94))


## v0.0.2 (2023-07-08)

### Fix

* fix(apps): setup.py

Added missing setup.py and fixed an if condition to allow the Worker
Manager Server to start in Linux systems ([`301c43f`](https://github.com/mibs510/OpenALPR-Webhook/commit/301c43f8465caf9f55b712c0fa6b46babfed003c))

### Unknown

* Merge remote-tracking branch &#39;origin/master&#39; ([`d8a99bd`](https://github.com/mibs510/OpenALPR-Webhook/commit/d8a99bd7c24635acb438d8aa3e256023f8004d6a))


## v0.0.1 (2023-07-07)

### Chore

* chore(requirements.txt): update

Updated requirements.txt

Signed-off-by: Connor &lt;connor@mcmillan.website&gt; ([`1f0d805`](https://github.com/mibs510/OpenALPR-Webhook/commit/1f0d80526ceb0a6eb554ad767ae5975594ce55cb))

### Documentation

* docs(README.md): Pre-release

Added pre-release notification and added worker management to known
bugs. ([`46429e9`](https://github.com/mibs510/OpenALPR-Webhook/commit/46429e9bdd53eaf2cac1b9c5d5bd75025f2f3e27))

* docs(Redis Workers): Reimplementation

Reimplementing redis server worker management using the multiprocessing
library. Not tested and not final. ([`9ceb4e7`](https://github.com/mibs510/OpenALPR-Webhook/commit/9ceb4e76e6f7db6209fa0811138e7c9c06f457d7))

* docs(README): Bare Server

Added build-essential &amp; python3-dev into the Bare Server section of the
README.md file ([`dc7097d`](https://github.com/mibs510/OpenALPR-Webhook/commit/dc7097d9ee82cdac55f4f9966b0a28e8917ceb3d))

### Fix

* fix(apps): Release-candidate

Fixed way too much stuff to feel confident in calling this the first
release. ([`a702c45`](https://github.com/mibs510/OpenALPR-Webhook/commit/a702c456f68b12f87f7a395f7b6ecd78c572646a))

### Unknown

* Initial commit ([`f1535e3`](https://github.com/mibs510/OpenALPR-Webhook/commit/f1535e3e786a7e269755fbf4c8a4c60454a22245))
