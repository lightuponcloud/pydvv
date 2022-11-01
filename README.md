Dotted Version Vector Sets
==========================

[![SWUbanner](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://github.com/vshymanskyy/StandWithUkraine/blob/main/docs/README.md)


This is an implementation of the Erlang's [DVV](https://github.com/ricardobcl/Dotted-Version-Vectors) on Python.

It is used in distributed systems, where UTC timestamp is unreliable value for object's version control.

Usage examples
==============

* Creating a new version
```python
from dvvset import DVVSet
dvvset = DVVSet()
dot = dvvset.create(dvvset.new("something"), "user_id_1")
```

* Incrementing version
```python
context = dvvset.join(dot)
new_dot = dvvset.update(dvvset.new_with_history(context, "something else"), dot, "user_id_2")
dvvset.sync([dot, new_dot])
```

* Detecting conflicts

Conflict is situation when two branches of the history exist.
It could happen when someone updates old version ( casual history ).

```python
merged_history = dvvset.sync([OldVersion, NewVersion])
if len(dvvset.values(merged_history)) > 1:
    print("Conflict detected")
else:
    print("Ok")
```

Example
=======
1. User 1 uploads file to the server, specifying version vector:
```python
from dvvset import DVVSet
dvvset = DVVSet()
dot = dvvset.create(dvvset.new("something"), "user_id_1")
```

2. Server checks version on a subject of conflict. Then it
stores file with version information and provides it to User 2.

```python
merged_history = dvvset.sync([ExistingVersion, UploadedVersion])
if len(dvvset.values(merged_history)) > 1:
    return "409 Conflict"
else:
    return "200 OK"  # Casual history is linear
```

3. User 2 downloads file, edits it and increments its version, before uploading back to server.

```python
context = dvvset.join(dot)  # ``dot`` is a downloaded version
new_dot = dvvset.update(dvvset.new_with_history(context, "something else"), dot, "user_id_2")
dvvset.sync([dot, new_dot])
```
