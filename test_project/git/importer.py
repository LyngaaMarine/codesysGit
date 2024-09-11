# We enable the new python 3 print syntax
from __future__ import print_function

import io
import json
import os
import re
import shutil
import sys
import time
import traceback


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
        print(text, "none/root")


def decodeMatch(match):
    return chr(int(match.group(1)))


def decodeObjectName(string):
    return re.sub(r"{(\d+)}", decodeMatch, string)


def fileContent(path):
    f = io.open(file=path, mode="r", encoding="utf-8")
    data = f.read()
    f.close()
    return data


def trueFind(object, name):
    children = object.get_children(False)
    if children:
        for child in children:
            if child.get_name() == name:
                return child


defferedEnable = []


def finishedDefferedEnable():
    for item in defferedEnable:
        item[0].exclude_from_build = item[1]


def applyObjectBuildProperties(object, propsSet, defferEnable):
    props = object.build_properties
    if props:
        if props.external_is_valid and "external" in propsSet:
            props.external = propsSet["external"]
        if props.enable_system_call_is_valid and "enable_system_call" in propsSet:
            props.enable_system_call = propsSet["enable_system_call"]
        if (
            props.compiler_defines_is_valid
            and "compiler_defines" in propsSet
            and len(propsSet["compiler_defines"]) > 0
        ):
            props.compiler_defines = propsSet["compiler_defines"]
        if props.link_always_is_valid and "link_always" in propsSet:
            props.link_always = propsSet["link_always"]
        if props.exclude_from_build_is_valid:
            if "exclude_from_build" in propsSet:
                props.exclude_from_build = propsSet["exclude_from_build"]
                # if defferEnable:
                #     props.exclude_from_build = True
                #     defferedEnable.append([props, propsSet["exclude_from_build"]])
                # else:
                #     props.exclude_from_build = False


def dictToDeviceId(dict):
    return DeviceID(dict["type"], dict["id"], dict["version"])


tempFilePath = ""


def writeTempFile(data):
    f = io.open(file=tempFilePath, mode="w", encoding="utf-8")
    f.write(data)
    f.close()


def writeDeclerationAndImplementationToObject(object, data, defferEnable):
    parts = data.split("!__DECLARATION__!\n", 1)
    applyObjectBuildProperties(object, json.loads(parts[0]), defferEnable)
    parts = parts[1].split("!__IMPLEMENTATION__!", 1)
    object.textual_declaration.replace(parts[0][:-1])
    if object.has_textual_implementation:
        object.textual_implementation.append(parts[1][1:])


# ###########################################################################################################################################
#    _____   ____  _    _
#   |  __ \ / __ \| |  | |
#   | |__) | |  | | |  | |
#   |  ___/| |  | | |  | |
#   | |    | |__| | |__| |
#   |_|     \____/ \____/
# ###########################################################################################################################################


def handlePOU(creationObject, name, path, ext):
    pou = creationObject.create_pou(name, PouType.Program)
    writeDeclerationAndImplementationToObject(pou, fileContent(path + ext), True)
    loopDir(pou, pou, path, False)


def handleDUT(creationObject, name, path, ext):
    pou = creationObject.create_dut(name, DutType.Structure)
    parts = fileContent(path + ext).split("!__DECLARATION__!\n", 1)
    applyObjectBuildProperties(pou, json.loads(parts[0]), True)
    pou.textual_declaration.replace(parts[1])
    loopDir(pou, pou, path, False)


def handleGVL(creationObject, name, path, ext):
    pou = creationObject.create_gvl(name)
    parts = fileContent(path + ext).split("!__DECLARATION__!\n", 1)
    applyObjectBuildProperties(pou, json.loads(parts[0]), True)
    pou.textual_declaration.replace(parts[1])
    loopDir(pou, pou, path, False)


def handleInterface(creationObject, name, path, ext):
    pou = creationObject.create_interface(name)
    parts = fileContent(path + ext).split("!__DECLARATION__!\n", 1)
    applyObjectBuildProperties(pou, json.loads(parts[0]), True)
    pou.textual_declaration.replace(parts[1])
    loopDir(pou, pou, path, False)


def handlePersistentVariables(creationObject, name, path, ext):
    creationObject.import_native(path + ext)
    pou = trueFind(creationObject, name)
    if pou:
        loopDir(pou, pou, path, False)


# ###########################################################################################################################################
#    _____   ____  _    _   __  __                _
#   |  __ \ / __ \| |  | | |  \/  |              | |
#   | |__) | |  | | |  | | | \  / | ___ _ __ ___ | |__   ___ _ __ ___
#   |  ___/| |  | | |  | | | |\/| |/ _ \ '_ ` _ \| '_ \ / _ \ '__/ __|
#   | |    | |__| | |__| | | |  | |  __/ | | | | | |_) |  __/ |  \__ \
#   |_|     \____/ \____/  |_|  |_|\___|_| |_| |_|_.__/ \___|_|  |___/
# ###########################################################################################################################################


def handleProperty(creationObject, placementObject, name, path, ext):
    pou = creationObject.create_property(name, "INT")
    if placementObject:
        pou.move(placementObject, -1)
    parts = fileContent(path + ext).split("!__DECLARATION__!\n", 1)
    applyObjectBuildProperties(pou, json.loads(parts[0]), True)
    parts = parts[1].split("!__GETTER__!", 1)
    pou.textual_declaration.replace(parts[0][:-1])
    parts = parts[1].split("!__SETTER__!", 1)
    getter = pou.find("Get")[0]
    if len(parts[0]) > 2:
        getparts = parts[0].split("!__IMPLEMENTATION__!", 1)
        getter.textual_declaration.replace(getparts[0][1:-1])
        if getter.has_textual_implementation:
            getter.textual_implementation.append(getparts[1][1:-1])
    else:
        getter.remove()
    setter = pou.find("Set")[0]
    if len(parts[1]) > 1:
        setparts = parts[1].split("!__IMPLEMENTATION__!", 1)
        setter.textual_declaration.replace(setparts[0][1:-1])
        if setter.has_textual_implementation:
            setter.textual_implementation.append(setparts[1][1:])
    else:
        setter.remove()


def handleAction(creationObject, placementObject, name, path, ext):
    pou = creationObject.create_action(name)
    parts = fileContent(path + ext).split("!__DECLARATION__!\n", 1)
    applyObjectBuildProperties(pou, json.loads(parts[0]), True)
    if placementObject:
        pou.move(placementObject)
    pou.textual_implementation.replace(parts[1])


def handleMethod(creationObject, placementObject, name, path, ext):
    pou = creationObject.create_method(name)
    if placementObject:
        pou.move(placementObject)
    writeDeclerationAndImplementationToObject(pou, fileContent(path + ext), True)


def handleTransition(creationObject, placementObject, name, path, ext):
    pou = creationObject.create_transition(name)
    parts = fileContent(path + ext).split("!__DECLARATION__!\n", 1)
    applyObjectBuildProperties(pou, json.loads(parts[0]), True)
    if placementObject:
        pou.move(placementObject)
    pou.textual_implementation.replace(parts[1])


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
def handleFolder(creationObject, placementObject, name, path, ext):
    creationObject.create_folder(name)
    finds = creationObject.find(name)
    if finds:
        self = finds[0]
        if self is None:
            self = trueFind(creationObject, name)
    if self:
        if placementObject:
            self.move(placementObject, -1)
        buildProps = json.loads(fileContent(path + ext))
        applyObjectBuildProperties(self, buildProps, False)
        if creationObject == placementObject:
            loopDir(creationObject, self, path, False)
        else:
            loopDir(self, None, path, False)


versionPattern1 = r"(\w|\d|\s)*, ((\d*\.){3}\d*|\*) \((\w|\d|\s)*\)"
versionPattern2 = r"(\w+), (\d+\.\d+\.\d+\.\d+) \((.+)\)"


def replace_version(match):
    part1 = match.group(1)
    part3 = match.group(3)
    return part1 + ", * (" + part3 + ")"


def handleLibraryManager(creationObject, path, ext):
    manager = creationObject.get_library_manager()
    jsonData = json.loads(fileContent(path + ext))
    for library in jsonData["libraries"]:
        if re.match(versionPattern1, library["Name"]):
            lib = librarymanager.find_library(
                re.sub(
                    versionPattern2,
                    replace_version,
                    library["Name"],
                )
            )
            if lib:
                manager.add_library(lib[0])
        else:
            lib = librarymanager.find_library(
                re.sub(
                    versionPattern2,
                    replace_version,
                    library["DefaultResolution"],
                )
            )
            if lib:
                manager.add_placeholder(library["Namespace"], lib[0])


def handleImagePool(creationObject, name, path, ext):
    jsonData = json.loads(fileContent(path + ext))
    extData = (
        """<ExportFile><StructuredView Guid="{21af5390-2942-461a-bf89-951aaf6999f1}"><Single xml:space="preserve" Type="{3daac5e4-660e-42e4-9cea-3711b98bfb63}" Method="IArchivable"><Null Name="Profile" /><List2 Name="EntryList"><Single Type="{6198ad31-4b98-445c-927f-3258a0e82fe3}" Method="IArchivable"><Single Name="IsRoot" Type="bool">True</Single><Single Name="MetaObject" Type="{81297157-7ec9-45ce-845e-84cab2b88ade}" Method="IArchivable"><Single Name="Guid" Type="System.Guid">f46998ba-2626-4ec2-9a83-574e14c52f23</Single><Single Name="ParentGuid" Type="System.Guid">00000000-0000-0000-0000-000000000000</Single><Single Name="Name" Type="string">"""
        + name
        + """</Single><Dictionary Type="{2c41fa04-1834-41c1-816e-303c7aa2c05b}" Name="Properties" /><Single Name="TypeGuid" Type="System.Guid">bb0b9044-714e-4614-ad3e-33cbdf34d16b</Single><Null Name="EmbeddedTypeGuids" /><Single Name="Timestamp" Type="long">0</Single></Single><Single Name="Object" Type="{bb0b9044-714e-4614-ad3e-33cbdf34d16b}" Method="IArchivable"><Single Name="UniqueIdGenerator" Type="string">10</Single><List Name="BitmapPool" Type="System.Collections.ArrayList">"""
    )
    for image in jsonData["imagepool"]:
        extData = (
            extData
            + """<Single Type="{215b2719-0347-4e4d-ba85-8bcd66946f66}" Method="IArchivable"><Single Name="BitmapID" Type="string">"""
            + image["id"]
            + """</Single><Single Name="FileID" Type="string">"""
            + image["fileID"]
            + """</Single><Single Name="ItemID" Type="int">"""
            + image["itemID"]
            + """</Single></Single>"""
        )
    extData = (
        extData
        + """</List><Single Name="GuidInit" Type="System.Guid">3e93a304-a5a8-4916-a921-3b0c3cf5c871</Single><Single Name="GuidReInit" Type="System.Guid">5a972ab1-fda5-44df-b529-8b164710d226</Single><Single Name="GuidExitX" Type="System.Guid">76be1e53-b9b5-43b7-b99c-51b7a1509208</Single><Single Name="ValidIds" Type="bool">True</Single></Single><Single Name="ParentSVNodeGuid" Type="System.Guid">00000000-0000-0000-0000-000000000000</Single><Array Name="Path" Type="string" /><Single Name="Index" Type="int">-1</Single></Single>"""
    )
    for image in jsonData["imagedata"]:
        extData = (
            extData
            + """<Single Type="{6198ad31-4b98-445c-927f-3258a0e82fe3}" Method="IArchivable"><Single Name="IsRoot" Type="bool">True</Single><Single Name="MetaObject" Type="{81297157-7ec9-45ce-845e-84cab2b88ade}" Method="IArchivable"><Single Name="Guid" Type="System.Guid">"""
            + image["guid"]
            + """</Single><Single Name="ParentGuid" Type="System.Guid">00000000-0000-0000-0000-000000000000</Single><Single Name="Name" Type="string">"""
            + image["name"]
            + """</Single><Dictionary Type="{2c41fa04-1834-41c1-816e-303c7aa2c05b}" Name="Properties" /><Single Name="TypeGuid" Type="System.Guid">9001d745-b9c5-4d77-90b7-b29c3f77a23b</Single><Null Name="EmbeddedTypeGuids" /><Single Name="Timestamp" Type="long">0</Single></Single><Single Name="Object" Type="{9001d745-b9c5-4d77-90b7-b29c3f77a23b}" Method="IArchivable"><Single Name="AutoUpdateMode" Type="string">"""
            + image["autoUpdateMode"]
            + """</Single><Array Name="Data" Type="byte">"""
            + image["data"]
            + """</Array><Single Name="LastModification" Type="System.DateTime">01/01/2000 01:01:01</Single><Single Name="Frozen" Type="bool">"""
            + image["frozen"]
            + """</Single></Single><Single Name="ParentSVNodeGuid" Type="System.Guid">00000000-0000-0000-0000-000000000000</Single><Array Name="Path" Type="string" /><Single Name="Index" Type="int">-1</Single></Single>"""
        )
    extData = (
        extData
        + """</List2><Null Name="ProfileName" /></Single></StructuredView></ExportFile>"""
    )
    writeTempFile(extData)
    creationObject.import_native(tempFilePath)


def handleTextList(creationObject, name, path, ext, isGlobal):
    print("Handling Text List: ", name)
    loaded = fileContent(path + ext)
    textListJson = json.loads(loaded)
    if isGlobal:
        typeGUID = "63784cbb-9ba0-45e6-9d69-babf3f040511"
    else:
        typeGUID = "2bef0454-1bd3-412a-ac2c-af0f31dbc40f"
    textList = """"""
    for textItem in textListJson["TextList"]:
        languages = (
            """<List Name="LanguageTexts" Type="System.Collections.ArrayList">"""
        )
        for langItems in textItem["LanguageTexts"]:
            languages = (
                languages + """<Single Type="string">""" + langItems + """</Single>"""
            )
        textList = (
            textList
            + """<Single Type="{53da1be7-ad25-47c3-b0e8-e26286dad2e0}" Method="IArchivable"><Single Name="TextID" Type="string">"""
            + str(textItem["TextID"])
            + """</Single><Single Name="TextDefault" Type="string">"""
            + textItem["TextDefault"]
            + """</Single>"""
            + languages
            + """</List></Single>"""
        )
    languageList = ""
    for langItems in textListJson["LanguageList"]:
        languageList = (
            languageList + """<Single Type="string">""" + langItems + """</Single>"""
        )
    extData = (
        """<ExportFile><StructuredView Guid="{21af5390-2942-461a-bf89-951aaf6999f1}"><Single xml:space="preserve" Type="{3daac5e4-660e-42e4-9cea-3711b98bfb63}" Method="IArchivable"><Null Name="Profile" /><List2 Name="EntryList"><Single Type="{6198ad31-4b98-445c-927f-3258a0e82fe3}" Method="IArchivable"><Single Name="IsRoot" Type="bool">True</Single><Single Name="MetaObject" Type="{81297157-7ec9-45ce-845e-84cab2b88ade}" Method="IArchivable"><Single Name="Guid" Type="System.Guid">94219ed4-c5bd-4d8b-af4f-4e345d98c65d</Single><Single Name="ParentGuid" Type="System.Guid">00000000-0000-0000-0000-000000000000</Single><Single Name="Name" Type="string">"""
        + name
        + """</Single><Dictionary Type="{2c41fa04-1834-41c1-816e-303c7aa2c05b}" Name="Properties" /><Single Name="TypeGuid" Type="System.Guid">"""
        + typeGUID
        + """</Single><Array Name="EmbeddedTypeGuids" Type="System.Guid" /><Single Name="Timestamp" Type="long">0</Single></Single><Single Name="Object" Type="{"""
        + typeGUID
        + """}" Method="IArchivable"><Single Name="UniqueIdGenerator" Type="string">0</Single><List Name="TextList" Type="System.Collections.ArrayList">"""
        + textList
        + """</List><List Name="Languages" Type="System.Collections.ArrayList">"""
        + languageList
        + """</List><Single Name="GuidInit" Type="System.Guid">5b0e1823-2581-4969-a09b-b5fab15da65a</Single><Single Name="GuidReInit" Type="System.Guid">ab41cbd1-b3fd-4a03-a7f2-7e9c62eaa18b</Single><Single Name="GuidExitX" Type="System.Guid">ab21c0f1-2032-4360-bbfd-2e5e86925933</Single></Single><Single Name="ParentSVNodeGuid" Type="System.Guid">00000000-0000-0000-0000-000000000000</Single><Array Name="Path" Type="string" /><Single Name="Index" Type="int">-1</Single></Single></List2><Null Name="ProfileName" /></Single></StructuredView></ExportFile>"""
    )
    writeTempFile(extData)
    creationObject.import_native(tempFilePath)


def handleSymbols(creationObject, path, ext):
    creationObject.import_native(path + ext)


# ###########################################################################################################################################
#   __      ___
#   \ \    / (_)
#    \ \  / / _ ___ _   _
#     \ \/ / | / __| | | |
#      \  /  | \__ \ |_| |
#       \/   |_|___/\__,_|
# ###########################################################################################################################################


def handleVisuManager(application, name, path, ext):
    application.import_native(path + ext)
    self = application.find(name)[0]
    loopDir(self, None, path, True)


# def handleWebVisu(visuManager, name, path, ext):
#     visuManager.import_native(path + ext)


def handleVisu(creationObject, path, ext):
    creationObject.import_native(path + ext)


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


def handleDevice(project, name, path, ext):
    finds = project.find(name)
    if len(finds) == 0:
        jsonData = json.loads(fileContent(path + ext))
        project.add(name, dictToDeviceId(jsonData["deviceID"]))
        plc = project.find(name)[0]
        loopDir(plc, plc, path, False)
    else:
        loopDir(finds[0], finds[0], path, False)


def handlePLCLogic(plc, name, path, ext):
    self = plc.find("Plc Logic")[0]
    buildProps = json.loads(fileContent(path + ext))
    applyObjectBuildProperties(self, buildProps, False)
    for child in self.get_children(False):
        child.remove()
    loopDir(self, None, path, False)


def handleApplication(plclogic, name, path, ext):
    plclogic.import_native(path + ext)
    self = plclogic.find(name)[0]
    loopDir(self, None, path, True)


def handleTaskConfiguration(application, name, path):
    self = application.find(name)
    if len(self) > 0:
        self[0].remove()
    self = application.create_task_configuration()
    loopDir(self, None, path, False)


kindsOfTasks = {
    "Cyclic": KindOfTask.Cyclic,
    "Freewheeling": KindOfTask.Freewheeling,
    "Event": KindOfTask.Event,
    "ExternalEvent": KindOfTask.ExternalEvent,
    "Status": KindOfTask.Status,
    "ParentSynchron": KindOfTask.ParentSynchron,
}


def handleTask(taskConfigurator, name, path, ext):
    self = taskConfigurator.create_task(name)
    buildProps = json.loads(fileContent(path + ext))
    self.kind_of_task = kindsOfTasks[buildProps["kindOfTask"]]
    self.priority = buildProps["priority"]
    self.core_binding = buildProps["coreBinding"]
    self.interval = buildProps["interval"]
    self.interval_unit = buildProps["intervalUnit"]
    self.event = buildProps["event"]
    self.external_event = buildProps["externalEvent"]
    self.parent_synchron_task = buildProps["parentSynchronTask"]
    watchDog = self.watchdog
    watchDog.enabled = buildProps["watchdog"]["enabled"]
    watchDog.time = buildProps["watchdog"]["time"]
    watchDog.time_unit = buildProps["watchdog"]["timeUnit"]
    watchDog.sensitivity = buildProps["watchdog"]["sensitivity"]
    pous = self.pous
    for pouProps in buildProps["pous"]:
        pous.add(pouProps["pou"], pouProps["comment"])

    loopDir(self, None, path, False)


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


def handleProjectSettings(plclogic, name, path, ext):
    plclogic.import_native(path + ext)


def handleProjectInformation(plclogic, name, path, ext):
    plclogic.import_native(path + ext)


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


def handleFile(creationObject, placementObject, path, file):
    search = re.search("%.+%", file)
    type = search.group()
    split = os.path.splitext(file[search.span()[1] :])
    objectname = decodeObjectName(split[0])
    ext = split[1]
    path = os.path.join(path, type + split[0])
    try:
        if type == "%F%" and ext == ".json":
            handleFolder(creationObject, placementObject, objectname, path, ext)
        # POU
        elif type == "%GVL%" and ext == ".st":
            handleGVL(creationObject, objectname, path, ext)
        elif type == "%PV%" and ext == ".xml":
            handlePersistentVariables(creationObject, objectname, path, ext)
        elif type == "%POU%" and ext == ".st":
            handlePOU(creationObject, objectname, path, ext)
        elif type == "%DUT%" and ext == ".st":
            handleDUT(creationObject, objectname, path, ext)
        elif type == "%ITF%" and ext == ".st":
            handleInterface(creationObject, objectname, path, ext)

        # POU Members
        elif type == "%PRO%" and ext == ".st":
            handleProperty(creationObject, placementObject, objectname, path, ext)
        elif type == "%ACT%" and ext == ".st":
            handleAction(creationObject, placementObject, objectname, path, ext)
        elif type == "%METH%" and ext == ".st":
            handleMethod(creationObject, placementObject, objectname, path, ext)
        elif type == "%TRAN%" and ext == ".st":
            handleTransition(creationObject, placementObject, objectname, path, ext)

        # Specials
        elif type == "%LIB%" and ext == ".json":  # Library Manager
            handleLibraryManager(creationObject, path, ext)
        elif type == "%IMP%" and ext == ".json":  # Image Pool
            handleImagePool(creationObject, objectname, path, ext)
        elif type == "%TL%" and ext == ".json":  # Text List
            handleTextList(creationObject, objectname, path, ext, False)
        elif type == "%SYM%" and ext == ".xml":  # Symbol Configuration
            handleSymbols(creationObject, path, ext)

        # # Visu
        elif type == "%VIMA%" and ext == ".xml":
            handleVisuManager(creationObject, objectname, path, ext)
        # elif type == "%WEVI%" and ext == ".xml":
        # Webvisu is skipped as they are included in the visu manager file
        #     handleWebVisu(creationObject, objectname, path, ext)
        elif type == "%VISU%" and ext == ".xml":
            handleVisu(creationObject, path, ext)

        # Device
        elif type == "%PLC%" and ext == ".json":
            handleDevice(creationObject, objectname, path, ext)
        elif type == "%PLOG%" and ext == ".json":
            handlePLCLogic(creationObject, objectname, path, ext)
        elif type == "%APP%" and ext == ".xml":
            handleApplication(creationObject, objectname, path, ext)
        elif type == "%TC%" and ext == ".json":
            handleTaskConfiguration(creationObject, objectname, path)
        elif type == "%TSK%" and ext == ".json":
            handleTask(creationObject, objectname, path, ext)

        # Project
        elif type == "%PS%" and ext == ".xml":
            handleProjectSettings(creationObject, objectname, path, ext)
        elif type == "%PI%" and ext == ".xml":
            handleProjectInformation(creationObject, objectname, path, ext)
        # elif type == "%GTL%" and ext == ".json":  # Global Text List
        #     handleTextList(creationObject, objectname, path, ext, True)

    except Exception as e:
        print("Error: ", e)
        print("Error in: ", objectname, path)
        traceback.print_exc()


objectOrder = [
    "%LIB%Library Manager.json",
    "%GTL%GlobalTextList.json",
    "%TC%Task configuration.xml",
    "%VIMA%Visualization Manager.xml",
]


def loopDir(creationObject, placementObject, path, sort):
    if os.path.exists(path):
        for root, dirs, files in os.walk(path):
            if sort:
                ordered = [element for element in objectOrder if element in files]
                ordered.extend(y for y in files if y not in ordered)
                files = ordered
            for file in files:
                handleFile(creationObject, placementObject, path, file)
            break


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

print(sys.argv[0])

structPath = os.path.dirname(os.path.dirname(sys.argv[0]))
projectPath = os.path.join(structPath, "project")
backupPath = os.path.join(structPath, "project_at_import")
srcPath = os.path.join(structPath, "src")
tempFilePath = os.path.join(structPath, "tempFile")

project = projects.primary

# Save project if open then close
if project is not None:
    project.save()
    project.close()

# Backup project
if not os.path.exists(backupPath):
    os.makedirs(backupPath)
if os.path.exists(os.path.join(projectPath, "src.project")):
    shutil.copyfile(
        os.path.join(projectPath, "src.project"),
        os.path.join(backupPath, "src.project"),
    )

# Delete project and create new
if os.path.exists(projectPath):
    shutil.rmtree(projectPath)
    os.makedirs(projectPath)

project = projects.create(os.path.join(projectPath, "src.project"), True)

#  Loops files in src directory
loopDir(project, None, srcPath, True)
# finishedDefferedEnable()

os.remove(tempFilePath)
