#!/usr/bin/env python3
"""Generate a minimal valid Xcode project for TromboneTuner.
Run this on Arch Linux (python3). It creates TromboneTuner.xcodeproj/
with a project.pbxproj that xcodebuild on GitHub Actions macOS can use.
"""

import os
import plistlib
from datetime import datetime

PROJECT_NAME = "TromboneTuner"
SRC_DIR = "TromboneTuner"
SWIFT_FILES = [
    "TromboneTunerApp.swift",
    "ContentView.swift",
    "TunerViewModel.swift",
    "PitchDetector.swift",
    "Note.swift",
]

# Object IDs (24 hex chars, Xcode-style)
def oid(suffix: str) -> str:
    return f"8A00000{suffix}23456789ABCDEF"


OBJ_PROJECT = oid("1")      # PBXProject
OBJ_MAIN_GROUP = oid("2")   # PBXGroup
OBJ_PRODUCTS_GROUP = oid("3")  # PBXGroup
OBJ_SOURCES_PHASE = oid("4")   # PBXSourcesBuildPhase
OBJ_TARGET = oid("5")       # PBXNativeTarget
OBJ_CONFIG_LIST = oid("6")  # XCConfigurationList
OBJ_DEBUG_CFG = oid("7")    # XCBuildConfiguration
OBJ_RELEASE_CFG = oid("8")  # XCBuildConfiguration
OBJ_PRODUCT_REF = oid("9")  # PBXProductReference

BUILD_FILE_IDS = [f"8A00002{i:02d}23456789ABCDEF" for i in range(len(SWIFT_FILES))]
FILE_REF_IDS = [f"8A00003{i:02d}23456789ABCDEF" for i in range(len(SWIFT_FILES))]


def pbx_group(name, children, isa="PBXGroup", source_tree="<group>", path=None):
    d = {
        "isa": isa,
        "children": children,
        "sourceTree": source_tree,
    }
    if name:
        d["name"] = name
    if path:
        d["path"] = path
    return d


def pbx_file_ref(name, path, last_known_type="sourcecode.swift"):
    return {
        "isa": "PBXFileReference",
        "lastKnownFileType": last_known_type,
        "name": name,
        "path": path,
        "sourceTree": "<group>",
    }


def pbx_build_file(file_ref_id):
    return {
        "isa": "PBXBuildFile",
        "fileRef": file_ref_id,
    }


objects = {}

# PBXProject
objects[OBJ_PROJECT] = {
    "isa": "PBXProject",
    "attributes": {
        "LastUpgradeCheck": 1500,
        "TargetAttributes": {
            OBJ_TARGET: {
                "CreatedOnToolsVersion": "15.0",
            }
        }
    },
    "buildConfigurationList": OBJ_CONFIG_LIST,
    "compatibilityVersion": "Xcode 15.0",
    "developmentRegion": "en",
    "hasScannedForEncodings": 0,
    "knownRegions": ["en"],
    "mainGroup": OBJ_MAIN_GROUP,
    "productRefGroup": OBJ_PRODUCTS_GROUP,
    "projectDirPath": "",
    "projectRoot": "",
    "targets": [OBJ_TARGET],
}

# PBXGroup (products)
products_group_children = []
product_ref_obj = {
    "isa": "PBXFileReference",
    "explicitFileType": "wrapper.application",
    "includeInIndex": 0,
    "path": f"{PROJECT_NAME}.app",
    "sourceTree": "BUILT_PRODUCTS_DIR",
}
objects[OBJ_PRODUCT_REF] = product_ref_obj
products_group_children.append(OBJ_PRODUCT_REF)

objects[OBJ_PRODUCTS_GROUP] = pbx_group("Products", products_group_children)

# PBXFileReference for each swift file + PBXBuildFile
source_children = []
build_files = []
for swift, file_ref_id, build_file_id in zip(SWIFT_FILES, FILE_REF_IDS, BUILD_FILE_IDS):
    path = f"{SRC_DIR}/{swift}"
    objects[file_ref_id] = pbx_file_ref(swift, path)
    source_children.append(file_ref_id)
    objects[build_file_id] = pbx_build_file(file_ref_id)
    build_files.append(build_file_id)

# PBXGroup (main group)
objects[OBJ_MAIN_GROUP] = pbx_group(None, source_children + [OBJ_PRODUCTS_GROUP])

# PBXSourcesBuildPhase
objects[OBJ_SOURCES_PHASE] = {
    "isa": "PBXSourcesBuildPhase",
    "buildActionMask": 2147483647,
    "files": build_files,
    "runOnlyForDeploymentPostprocessing": 0,
}

# XCBuildConfiguration (shared base)
base_build_settings = {
    "CODE_SIGN_IDENTITY": "",
    "CODE_SIGNING_ALLOWED": "NO",
    "DEBUG_INFORMATION_FORMAT": "dwarf",
    "INFOPLIST_FILE": f"{SRC_DIR}/Info.plist",
    "IPHONEOS_DEPLOYMENT_TARGET": "16.0",
    "LD_RUNPATH_SEARCH_PATHS": ["$(inherited)", "@executable_path/Frameworks"],
    "PRODUCT_BUNDLE_IDENTIFIER": "com.carte.trombonetuner",
    "PRODUCT_NAME": "$(TARGET_NAME)",
    "SDKROOT": "iphoneos",
    "SUPPORTED_PLATFORMS": ["iphoneos", "iphonesimulator"],
    "TARGETED_DEVICE_FAMILY": "1,2",
}

debug_settings = dict(base_build_settings)
debug_settings.update({
    "DEBUG_INFORMATION_FORMAT": "dwarf",
})

release_settings = dict(base_build_settings)
release_settings.update({
    "DEBUG_INFORMATION_FORMAT": "dwarf-with-dsym",
})

objects[OBJ_DEBUG_CFG] = {
    "isa": "XCBuildConfiguration",
    "buildSettings": debug_settings,
    "name": "Debug",
}
objects[OBJ_RELEASE_CFG] = {
    "isa": "XCBuildConfiguration",
    "buildSettings": release_settings,
    "name": "Release",
}

# XCConfigurationList
objects[OBJ_CONFIG_LIST] = {
    "isa": "XCConfigurationList",
    "buildConfigurations": [OBJ_DEBUG_CFG, OBJ_RELEASE_CFG],
    "defaultConfigurationIsVisible": 0,
    "defaultConfigurationName": "Release",
}

# PBXNativeTarget
objects[OBJ_TARGET] = {
    "isa": "PBXNativeTarget",
    "buildConfigurationList": OBJ_CONFIG_LIST,
    "buildPhases": [OBJ_SOURCES_PHASE],
    "buildRules": [],
    "dependencies": [],
    "name": PROJECT_NAME,
    "productName": PROJECT_NAME,
    "productReference": OBJ_PRODUCT_REF,
    "productType": "com.apple.product-type.application",
}

root_object = {
    "archiveVersion": 1,
    "classes": {},
    "objectVersion": 52,
    "objects": objects,
    "rootObject": OBJ_PROJECT,
}

# Write pbxproj as binary plist (Xcode-native)
proj_dir = f"{PROJECT_NAME}.xcodeproj"
os.makedirs(proj_dir, exist_ok=True)

pbxproj_path = os.path.join(proj_dir, "project.pbxproj")
with open(pbxproj_path, "wb") as f:
    plistlib.dump(root_object, f, fmt=plistlib.FMT_BINARY)

# Workspace file
workspace_dir = f"{PROJECT_NAME}.xcworkspace"
os.makedirs(workspace_dir, exist_ok=True)
with open(os.path.join(workspace_dir, "contents.xcworkspacedata"), "w") as f:
    f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write(f'<Workspace>\n')
    f.write(f'   <fileRef ref="{PROJECT_NAME}.xcodeproj"/>\n')
    f.write(f'</Workspace>\n')

# Minimal Info.plist
info_plist = {
    "CFBundleDevelopmentRegion": "$(DEVELOPMENT_LANGUAGE)",
    "CFBundleExecutable": "$(EXECUTABLE_NAME)",
    "CFBundleIdentifier": "$(PRODUCT_BUNDLE_IDENTIFIER)",
    "CFBundleInfoDictionaryVersion": "6.0",
    "CFBundleName": "$(PRODUCT_NAME)",
    "CFBundlePackageType": "APPL",
    "CFBundleShortVersionString": "1.0",
    "CFBundleVersion": "1",
    "LSRequiresIPhoneOS": True,
    "NSMicrophoneUsageDescription": "TromboneTuner needs microphone access to detect pitch.",
    "UIRequiredDeviceCapabilities": ["arm64"],
    "UISupportedInterfaceOrientations": ["UIInterfaceOrientationPortrait"],
}
os.makedirs(SRC_DIR, exist_ok=True)
with open(os.path.join(SRC_DIR, "Info.plist"), "wb") as f:
    plistlib.dump(info_plist, f, fmt=plistlib.FMT_BINARY)

print(f"Created {proj_dir}/")
print(f"Created {workspace_dir}/")
print(f"Created {SRC_DIR}/Info.plist")
print()
print("Commit these to GitHub along with the .swift files and .github/workflows/ios.yml")
print("Then run the Actions workflow on the macos-latest runner to get your unsigned .ipa")
