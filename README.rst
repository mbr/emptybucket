Small python script that empties amazon AWS buckets and deletes them, fast.

Requires: python-progressbar (Install "progressbar" via pip)
          boto

Example:
python emptybucket.py --key your_aws_key --secret-key your_aws_secret_key
myfancybucket

If any of the key options isn't present, the script will prompt for them.

No brakes, no confirmations, no guarantees.
