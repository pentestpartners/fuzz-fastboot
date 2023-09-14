usage: fuzz-fastboot.py [-h] [-l [LOG]] [-a [AVOID]] [-b [BASE]] [-f [MATCH_FAIL]] dictionary

positional arguments:
  dictionary            Dictionary of commands

optional arguments:
  -h, --help            show this help message and exit
  -l [LOG], --log [LOG]
                        Log to file
  -a [AVOID], --avoid [AVOID]
                        File of words to avoid
  -b [BASE], --base [BASE]
                        Base command, e.g. "oem"
  -f [MATCH_FAIL], --match_fail [MATCH_FAIL]
                        Match string for failure

