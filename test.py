from __future__ import print_function

import inspect

print(projects.primary.get_project_info())

# Get a list of all members of the example_object
members = inspect.getmembers(projects.primary)

# Print each member
for member in members:
    print(member)
