from __future__ import print_function

project = projects.primary
print(project.get_project_info())
print(project.get_project_info().__class__)

for test in dir(projects.__class__):
    print(test)

# print(projects.primary)
# print(projects.primary.get_children())
# print(projects.primary.get_project_info())

# # Get a list of all members of the example_object
# members = projects.primary

# res = project.add("Test", DeviceID(4096, "1006 1104", "6.3.0.12"))
# print(res)

# Print each member
# for member in project.get_children():
#     print(member)
#     print(member.type)
#     print(member.get_name())

# finds = project.find("_750_8110_PFC100_ECO")[0]
# print(finds)
# print(finds.get_device_identification())
# print(DeviceID(4096, "1006 1104", "6.3.0.12"))

# project.insert("Test", 0, DeviceID(4096, "1006 1104", "6.3.0.12"))

# Print each member
# for member in finds.get_children():
#     print(member.type)
#     print(member.get_name())


# finds = project.find("PFC100_2ETH_ECO")[0]
# print(finds)
