# We enable the new python 3 print syntax
from __future__ import print_function

import io
import json
import os
import re
import shutil
import sys
import time
import xml.etree.ElementTree as ET


# ###########################################################################################################################################
#    _    _      _
#   | |  | |    | |
#   | |__| | ___| |_ __   ___ _ __ ___
#   |  __  |/ _ \ | '_ \ / _ \ '__/ __|
#   | |  | |  __/ | |_) |  __/ |  \__ \
#   |_|  |_|\___|_| .__/ \___|_|  |___/
#                 | |
#                 |_|
# ###########################################################################################################################################
def tryPrintObjectName(text, obj):
    try:
        print(text, obj.get_name())
    except:
        print(text, "root")


def encodeMatch(match):
    return "{" + str(ord(match.group(0))) + "}"


def encodeObjectName(object):
    name = re.sub(r"[^A-Za-z0-9 _-]", encodeMatch, object.get_name()).rstrip()
    return name


def writeDataToFileUTF8(data, path):
    f = io.open(file=path, mode="w", newline="\n", encoding="utf-8")
    f.write(data.encode().decode("unicode_escape"))
    f.close()


def getObjectBuildProperties(object):
    list = {}
    props = object.build_properties
    if props:
        if props.external_is_valid:
            list["external"] = props.external
        if props.enable_system_call_is_valid:
            list["enable_system_call"] = props.enable_system_call
        if props.compiler_defines_is_valid:
            list["compiler_defines"] = props.compiler_defines
        if props.link_always_is_valid:
            list["link_always"] = props.link_always
        if props.exclude_from_build_is_valid:
            list["exclude_from_build"] = props.exclude_from_build
    return list


def deviceIDToDict(deviceID):
    return {
        "type": deviceID.type,
        "id": deviceID.id,
        "version": deviceID.version,
    }


def fileContent(path):
    f = open(path, "r")
    data = f.read()
    f.close()
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
        return data.decode("utf-8")
    return data


def writeDataToFile(data, path):
    with io.open(path, "w", newline="\n", encoding="utf-8") as f:
        f.write(data)


timeStampFinder = re.compile(
    r"(<Single Name=\"Timestamp\" Type=\"long\">)(\d+)(<\/Single>)"
)


def handleNativeExport(object, path, recursive):
    object.export_native(path, recursive)
    editedFile = timeStampFinder.sub("\\1 0 \\3", fileContent(path))
    writeDataToFile(editedFile, path)


def textExportDeclImpl(object, path):
    with io.open(path + ".st", "w", newline="\n", encoding="utf-8") as f:
        f.write(
            json.dumps(getObjectBuildProperties(object), indent=2)
            + "\n!__DECLARATION__!\n"
        )
        if object.has_textual_declaration:
            f.write(object.textual_declaration.text)
        f.write("\n!__IMPLEMENTATION__!\n")
        if object.has_textual_implementation:
            f.write(object.textual_implementation.text)


def textExportDecl(object, path):
    with io.open(path + ".st", "w", newline="\n", encoding="utf-8") as f:
        f.write(
            json.dumps(getObjectBuildProperties(object), indent=2)
            + "\n!__DECLARATION__!\n"
        )
        if object.has_textual_declaration:
            f.write(object.textual_declaration.text)


def textExportImpl(object, path):
    with io.open(path + ".st", "w", newline="\n", encoding="utf-8") as f:
        f.write(
            json.dumps(getObjectBuildProperties(object), indent=2)
            + "\n!__DECLARATION__!\n"
        )
        if object.has_textual_implementation:
            f.write(object.textual_implementation.text)


# ###########################################################################################################################################
#    _____   ____  _    _
#   |  __ \ / __ \| |  | |
#   | |__) | |  | | |  | |
#   |  ___/| |  | | |  | |
#   | |    | |__| | |__| |
#   |_|     \____/ \____/
# ###########################################################################################################################################


def handleTextType(object, path, designator):
    path = os.path.join(path, designator + encodeObjectName(object))
    if designator == "%POU%":
        textExportDeclImpl(object, path)
    elif designator == "%METH%":
        textExportDeclImpl(object, path)
    elif designator == "%TRAN%":
        textExportImpl(object, path)
    else:
        textExportDecl(object, path)
    loopObjects(object, path)


def handleProperty(object, path):
    path = os.path.join(path, "%PRO%" + encodeObjectName(object))
    with io.open(path + ".st", "w", newline="\n", encoding="utf-8") as f:
        f.write(
            json.dumps(getObjectBuildProperties(object), indent=2)
            + "\n!__DECLARATION__!\n"
        )
        if object.has_textual_declaration:
            f.write(object.textual_declaration.text.encode("utf-8"))
        f.write("\n!__GETTER__!\n")
        get = object.find("Get")
        if len(get) > 0:
            getter = get[0]
            if getter:
                if getter.has_textual_declaration:
                    f.write(getter.textual_declaration.text.encode("utf-8"))
                f.write("\n!__IMPLEMENTATION__!\n")
                if getter.has_textual_implementation:
                    f.write(getter.textual_implementation.text.encode("utf-8"))
        f.write("\n!__SETTER__!\n")
        set = object.find("Set")
        if len(set) > 0:
            setter = set[0]
            if setter:
                if setter.has_textual_declaration:
                    f.write(setter.textual_declaration.text.encode("utf-8"))
                f.write("\n!__IMPLEMENTATION__!\n")
                if setter.has_textual_implementation:
                    f.write(setter.textual_implementation.text.encode("utf-8"))


def handlePersistentVariables(object, path):
    path = os.path.join(path, "%PV%" + encodeObjectName(object))
    handleNativeExport(object, path + ".xml", False)
    loopObjects(object, path)


# ###########################################################################################################################################
#     _____                 _       _
#    / ____|               (_)     | |
#   | (___  _ __   ___  ___ _  __ _| |___
#    \___ \| '_ \ / _ \/ __| |/ _` | / __|
#    ____) | |_) |  __/ (__| | (_| | \__ \
#   |_____/| .__/ \___|\___|_|\__,_|_|___/
#          | |
#          |_|
# ###########################################################################################################################################
# Folder
def handleFolder(object, path):
    path = os.path.join(path, "%F%" + encodeObjectName(object))
    writeDataToFileUTF8(
        json.dumps(getObjectBuildProperties(object), indent=2), path + ".json"
    )
    loopObjects(object, path)


def handleLibrary(object, path):
    path = os.path.join(path, "%LIB%" + encodeObjectName(object))
    object.export_xml(
        reporter=None,
        path=path + ".xml",
        recursive=False,
        export_folder_structure=False,
        declarations_as_plaintext=True,
    )
    root = ET.fromstring(fileContent(path + ".xml"))
    os.remove(path + ".xml")

    libraries = []
    namespaces = {"ns": "http://www.plcopen.org/xml/tc6_0200"}
    for library in root.findall(".//ns:Library", namespaces):
        system_library = library.get("SystemLibrary")
        if system_library != "true":
            libraries.append(library.attrib)
    dict = getObjectBuildProperties(object)
    dict["libraries"] = libraries
    writeDataToFileUTF8(json.dumps(dict, indent=2), path + ".json")


def handleImagePool(object, path):
    path = os.path.join(path, "%IMP%" + encodeObjectName(object))
    object.export_native(path + ".xml", False)
    tree = ET.parse(path + ".xml")
    os.remove(path + ".xml")
    root = tree.getroot()
    list = {
        "BuildProperties": getObjectBuildProperties(object),
        "imagepool": [],
        "imagedata": [],
    }
    imageList = root.find(
        './StructuredView/Single/List2/Single/Single[@Name="Object"]/List[@Name="BitmapPool"]'
    )
    for item in imageList:
        id = item.find('./Single[@Name="BitmapID"]').text
        if id:
            list["imagepool"].append(
                {
                    "id": id,
                    "fileID": item.find('./Single[@Name="FileID"]').text or "",
                    "itemID": item.find('./Single[@Name="ItemID"]').text or "",
                }
            )
    imageData = root.findall(
        './StructuredView/Single/List2/Single[@Type="{6198ad31-4b98-445c-927f-3258a0e82fe3}"]'
    )
    for item in imageData:
        updateMode = item.find(
            './Single[@Name="Object"]/Single[@Name="AutoUpdateMode"]'
        )
        if updateMode is not None:
            list["imagedata"].append(
                {
                    "name": item.find(
                        './Single[@Name="MetaObject"]/Single[@Name="Name"]'
                    ).text
                    or "",
                    "guid": item.find(
                        './Single[@Name="MetaObject"]/Single[@Name="Guid"]'
                    ).text
                    or "",
                    "autoUpdateMode": updateMode.text or "",
                    "data": item.find(
                        './Single[@Name="Object"]/Array[@Name="Data"]'
                    ).text
                    or "",
                    "frozen": item.find(
                        './Single[@Name="Object"]/Single[@Name="Frozen"]'
                    ).text
                    or "",
                }
            )
    writeDataToFile(json.dumps(list, indent=2), path + ".json")


import codecs


def handleTextList(object, path, isGlobal):
    if isGlobal:
        path = os.path.join(path, "%GTL%" + encodeObjectName(object))
    else:
        path = os.path.join(path, "%TL%" + encodeObjectName(object))
    allInfo = {
        "BuildProperties": getObjectBuildProperties(object),
        "TextList": [],
        "LanguageList": [],
    }
    for row in object.rows:
        texts = []
        for i in range(row.languagetextcount()):
            cleaned_text = re.sub(r"\r+\n", "\r\n", row.languagetext(i))
            texts.append(cleaned_text)
        cleaned_text = re.sub(r"\r+\n", "\r\n", row.defaulttext)
        allInfo["TextList"].append(
            {
                "TextID": row.id,
                "TextDefault": cleaned_text,
                "LanguageTexts": texts,
            }
        )
    for i in range(object.languagecount()):
        allInfo["LanguageList"].append(object.getlanguage(i))
    json_data = json.dumps(allInfo, indent=2, ensure_ascii=False)
    with codecs.open(path + ".json", "w", encoding="utf-8") as file:
        file.write(json_data)


def handleSymbols(object, path):
    handleNativeExport(
        object, os.path.join(path, "%SYM%" + encodeObjectName(object)) + ".xml", False
    )


# ###########################################################################################################################################
#   __      ___
#   \ \    / (_)
#    \ \  / / _ ___ _   _
#     \ \/ / | / __| | | |
#      \  /  | \__ \ |_| |
#       \/   |_|___/\__,_|
# ###########################################################################################################################################


def handleVisualizationManager(object, path):
    path = os.path.join(path, "%VIMA%" + encodeObjectName(object))
    handleNativeExport(object, path + ".xml", True)
    loopObjects(object, path)


def handleWebVisu(object, path):
    handleNativeExport(
        object, os.path.join(path, "%WEVI%" + encodeObjectName(object)) + ".xml", True
    )


def handleVisualization(object, path):
    handleNativeExport(
        object, os.path.join(path, "%VISU%" + encodeObjectName(object)) + ".xml", False
    )


# ###########################################################################################################################################
#    _____             _
#   |  __ \           (_)
#   | |  | | _____   ___  ___ ___
#   | |  | |/ _ \ \ / / |/ __/ _ \
#   | |__| |  __/\ V /| | (_|  __/
#   |_____/ \___| \_/ |_|\___\___|
#
#
# ###########################################################################################################################################
# PLC
def handlePLC(object, path):
    path = os.path.join(path, "%PLC%" + encodeObjectName(object))
    deviceID = object.get_device_identification()
    props = getObjectBuildProperties(object)
    props["deviceID"] = deviceIDToDict(deviceID)
    props["allowSymbolicVarAccessInSyncWithIECCycle"] = (
        object.allow_symbolic_var_access_in_sync_with_iec_cycle
    )
    writeDataToFileUTF8(json.dumps(props, indent=2), path + ".json")
    loopObjects(object, path)


def handlePLCLogic(object, path):
    path = os.path.join(path, "%PLOG%" + encodeObjectName(object))
    writeDataToFileUTF8(
        json.dumps(getObjectBuildProperties(object), indent=2), path + ".json"
    )
    loopObjects(object, path)


def handleApplication(object, path):
    path = os.path.join(path, "%APP%" + encodeObjectName(object))
    handleNativeExport(object, path + ".xml", False)
    loopObjects(object, path)


def handleTaskConfiguration(object, path):
    path = os.path.join(path, "%TC%" + encodeObjectName(object))
    writeDataToFileUTF8(
        json.dumps(getObjectBuildProperties(object), indent=2), path + ".json"
    )
    loopObjects(object, path)


kindsOfTasks = [
    "None",
    "Cyclic",
    "Freewheeling",
    "Event",
    "ExternalEvent",
    "Status",
    "ParentSynchron",
]


def handleTask(object, path):
    path = os.path.join(path, "%TSK%" + encodeObjectName(object))
    dict = getObjectBuildProperties(object)
    kindOfTask = int(object.kind_of_task)
    dict["kindOfTask"] = kindsOfTasks[kindOfTask]
    dict["priority"] = object.priority
    dict["coreBinding"] = object.core_binding
    dict["interval"] = object.interval
    dict["intervalUnit"] = object.interval_unit
    dict["event"] = object.event
    dict["externalEvent"] = object.external_event
    dict["event"] = object.event
    dict["parentSynchronTask"] = object.parent_synchron_task
    watchDog = object.watchdog
    dict["watchdog"] = {
        "enabled": watchDog.enabled,
        "time": watchDog.time,
        "timeUnit": watchDog.time_unit,
        "sensitivity": watchDog.sensitivity,
    }
    pous = []
    for i in range(len(object.pous)):
        pous.append({"pou": object.pous[i][0], "comment": object.pous[i][1]})
    dict["pous"] = pous
    writeDataToFileUTF8(json.dumps(dict, indent=2), path + ".json")


# ###########################################################################################################################################
#    _____           _           _
#   |  __ \         (_)         | |
#   | |__) | __ ___  _  ___  ___| |_
#   |  ___/ '__/ _ \| |/ _ \/ __| __|
#   | |   | | | (_) | |  __/ (__| |_
#   |_|   |_|  \___/| |\___|\___|\__|
#                  _/ |
#                 |__/
# ###########################################################################################################################################


def handleProjectSettings(object, path):
    handleNativeExport(
        object, os.path.join(path, "%PS%" + encodeObjectName(object)) + ".xml", False
    )


def handleProjectInformation(object, path):
    handleNativeExport(
        object, os.path.join(path, "%PI%" + encodeObjectName(object)) + ".xml", False
    )


# def handleVisuStyle(object, path):
#     handleNativeExport(
#         object, os.path.join(path, "%VS%VisualizationStyle") + ".xml", False
#     )


# ###########################################################################################################################################
#    _
#   | |
#   | |     ___   ___  _ __   ___ _ __ ___
#   | |    / _ \ / _ \| '_ \ / _ \ '__/ __|
#   | |___| (_) | (_) | |_) |  __/ |  \__ \
#   |______\___/ \___/| .__/ \___|_|  |___/
#                     | |
#                     |_|
# ###########################################################################################################################################
# Loopers
def handleObject(object, path):
    type = str(object.type)
    if type == "738bea1e-99bb-4f04-90bb-a7a567e74e3a":  # Folder
        handleFolder(object, path)

    # POU
    elif type == "ffbfa93a-b94d-45fc-a329-229860183b1d":  # GVL
        handleTextType(object, path, "%GVL%")
    elif type == "261bd6e6-249c-4232-bb6f-84c2fbeef430":  # Persisten Vars
        handlePersistentVariables(object, path)
    elif type == "6f9dac99-8de1-4efc-8465-68ac443b7d08":  # POU
        handleTextType(object, path, "%POU%")
    elif (
        type == "2db5746d-d284-4425-9f7f-2663a34b0ebc"
        or type == "40989022-e4d2-4dc7-89d2-9a412930b20e"
    ):  # DUT
        handleTextType(object, path, "%DUT%")
    elif type == "6654496c-404d-479a-aad2-8551054e5f1e":  # ITF
        handleTextType(object, path, "%ITF%")

    # POU Members
    elif type == "8ac092e5-3128-4e26-9e7e-11016c6684f2":  # POU Action
        handleTextType(object, path, "%ACT%")
    elif type == "f8a58466-d7f6-439f-bbb8-d4600e41d099":  # POU Method
        handleTextType(object, path, "%METH%")
    elif type == "5a3b8626-d3e9-4f37-98b5-66420063d91e":  # POU Property
        handleProperty(object, path)
    elif type == "a10c6218-cb94-436f-91c6-e1652575253d":  # POU Transition
        handleTextType(object, path, "%TRAN%")
    elif type == "f89f7675-27f1-46b3-8abb-b7da8e774ffd":  # ITF Method
        handleTextType(object, path, "%METH%")
    elif type == "5a3b8626-d3e9-4f37-98b5-66420063d91e":  # ITF Property
        handleProperty(object, path)

    # Specials
    elif type == "adb5cb65-8e1d-4a00-b70a-375ea27582f3":  # Library Manager
        handleLibrary(object, path)
    elif type == "bb0b9044-714e-4614-ad3e-33cbdf34d16b":  # ImagePool
        handleImagePool(object, path)
    elif type == "21d4fe94-4123-4e23-9091-ead220afbd1f":  # Symbol Configuration
        handleSymbols(object, path)
    elif type == "2bef0454-1bd3-412a-ac2c-af0f31dbc40f":  # TextList
        handleTextList(object, path, False)

    # Visu
    elif type == "4d3fdb8f-ab50-4c35-9d3a-d4bb9bb9a628":  # Visualization Manager
        handleVisualizationManager(object, path)
    # elif type == "0fdbf158-1ae0-47d9-9269-cd84be308e9d":  # Visualization Manager
    # Webvisu is skipped as they are included in the visu manager file
    #     handleWebVisu(object, path)
    elif type == "f18bec89-9fef-401d-9953-2f11739a6808":  # Visualization
        handleVisualization(object, path)

    # Device
    elif type == "225bfe47-7336-4dbc-9419-4105a7c831fa":  # PLC
        handlePLC(object, path)
    elif type == "40b404f9-e5dc-42c6-907f-c89f4a517386":  # PLC Logic
        handlePLCLogic(object, path)
    elif type == "639b491f-5557-464c-af91-1471bac9f549":  # Application
        handleApplication(object, path)
    elif type == "ae1de277-a207-4a28-9efb-456c06bd52f3":  # Task Configuration
        handleTaskConfiguration(object, path)
    elif type == "98a2708a-9b18-4f31-82ed-a1465b24fa2d":  # Task
        handleTask(object, path)

    # Project
    elif type == "8753fe6f-4a22-4320-8103-e553c4fc8e04":  # Project Settings
        handleProjectSettings(object, path)
    elif type == "085afe48-c5d8-4ea5-ab0d-b35701fa6009":  # Project Information
        handleProjectInformation(object, path)
    # elif type == "8e687a04-7ca7-42d3-be06-fcbda676c5ef":  # VisualizationStyle
    # Visustyle does not work and does not seem to do anything
    #     handleVisuStyle(object, path)
    # elif type == "63784cbb-9ba0-45e6-9d69-babf3f040511":  # GlobalTextList
    #     return ""
    # global text list is skipped due to it being generated automatically
    # handleTextList(object, path, True)


def loopObjects(object, path):
    children = object.get_children(False)
    if len(children) > 0:
        if not os.path.exists(path):
            os.makedirs(path)
        for child in children:
            handleObject(child, path)


#######################################################################
#     _____           _       _      _____ _             _
#    / ____|         (_)     | |    / ____| |           | |
#   | (___   ___ _ __ _ _ __ | |_  | (___ | |_ __ _ _ __| |_ ___
#    \___ \ / __| '__| | '_ \| __|  \___ \| __/ _` | '__| __/ __|
#    ____) | (__| |  | | |_) | |_   ____) | || (_| | |  | |_\__ \
#   |_____/ \___|_|  |_| .__/ \__| |_____/ \__\__,_|_|   \__|___/
#                      | |
#                      |_|
#######################################################################
print("Exporter V0.0.3")

if projects.primary is None:
    structPath = os.path.dirname(os.path.dirname(sys.argv[0]))
else:
    structPath = os.path.dirname(os.path.dirname(projects.primary.path))

projectPath = os.path.join(structPath, "project")
backupPath = os.path.join(structPath, "project_at_export")
srcPath = os.path.join(structPath, "src")

project = projects.primary
if project is None:
    project = projects.open(os.path.join(projectPath, "src.project"))

project.save()

if not os.path.exists(backupPath):
    os.makedirs(backupPath)
if os.path.exists(os.path.join(projectPath, "src.project")):
    shutil.copyfile(
        os.path.join(projectPath, "src.project"),
        os.path.join(backupPath, "src.project"),
    )

if os.path.exists(srcPath):
    shutil.rmtree(srcPath)

# Loop all project objects
loopObjects(project, srcPath)
