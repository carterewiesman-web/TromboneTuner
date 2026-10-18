#!/usr/bin/env python3
import os
import plistlib
import uuid

PROJECT_NAME = "TromboneTuner"
SRC_DIR = "TromboneTuner"
SWIFT_FILES = [
    "TromboneTunerApp.swift",
    "ContentView.swift",
    "TunerViewModel.swift",
    "PitchDetector.swift",
    "Note.swift",
]

def make_id():
    return str(uuid.uuid4()).upper().replace('-', '')[:24]

# Generate all IDs
ids = {}
for name in ['project', 'mainGroup', 'productsGroup', 'sourcesPhase', 'target', 'configList', 'debugCfg', 'releaseCfg', 'productRef']:
    ids[name] = make_id()
for i, _ in enumerate(SWIFT_FILES):
    ids[f'fileRef{i}'] = make_id()
    ids[f'buildFile{i}'] = make_id()

objects = {}
objects[ids['project']] = {
    'isa': 'PBXProject',
    'attributes': {
        'LastUpgradeCheck': 1500,
        'TargetAttributes': {ids['target']: {'CreatedOnToolsVersion': '15.0'}}
    },
    'buildConfigurationList': ids['configList'],
    'compatibilityVersion': 'Xcode 15.0',
    'developmentRegion': 'en',
    'hasScannedForEncodings': 0,
    'knownRegions': ['en'],
    'mainGroup': ids['mainGroup'],
    'productRefGroup': ids['productsGroup'],
    'projectDirPath': '',
    'projectRoot': '',
    'targets': [ids['target']],
}

objects[ids['productRef']] = {
    'isa': 'PBXFileReference',
    'explicitFileType': 'wrapper.application',
    'includeInIndex': 0,
    'path': f'{PROJECT_NAME}.app',
    'sourceTree': 'BUILT_PRODUCTS_DIR',
}
objects[ids['productsGroup']] = {
    'isa': 'PBXGroup',
    'children': [ids['productRef']],
    'name': 'Products',
    'sourceTree': '<group>',
}

# Files
file_children = []
build_files = []
for i, fname in enumerate(SWIFT_FILES):
    objects[ids[f'fileRef{i}']] = {
        'isa': 'PBXFileReference',
        'lastKnownFileType': 'sourcecode.swift',
        'name': fname,
        'path': f'{SRC_DIR}/{fname}',
        'sourceTree': '<group>',
    }
    file_children.append(ids[f'fileRef{i}'])
    objects[ids[f'buildFile{i}']] = {
        'isa': 'PBXBuildFile',
        'fileRef': ids[f'fileRef{i}'],
    }
    build_files.append(ids[f'buildFile{i}'])

objects[ids['mainGroup']] = {
    'isa': 'PBXGroup',
    'children': file_children + [ids['productsGroup']],
    'sourceTree': '<group>',
}

objects[ids['sourcesPhase']] = {
    'isa': 'PBXSourcesBuildPhase',
    'buildActionMask': 2147483647,
    'files': build_files,
    'runOnlyForDeploymentPostprocessing': 0,
}

base_settings = {
    'CODE_SIGN_IDENTITY': '',
    'CODE_SIGNING_ALLOWED': 'NO',
    'DEVELOPMENT_TEAM': '',
    'INFOPLIST_FILE': f'{SRC_DIR}/Info.plist',
    'IPHONEOS_DEPLOYMENT_TARGET': '16.0',
    'LD_RUNPATH_SEARCH_PATHS': ['$(inherited)', '@executable_path/Frameworks'],
    'PRODUCT_BUNDLE_IDENTIFIER': 'com.carte.trombonetuner',
    'PRODUCT_NAME': '$(TARGET_NAME)',
    'SDKROOT': 'iphoneos',
    'SUPPORTED_PLATFORMS': 'iphoneos',
    'TARGETED_DEVICE_FAMILY': '1,2',
    'ONLY_ACTIVE_ARCH': 'YES',
}

objects[ids['debugCfg']] = {
    'isa': 'XCBuildConfiguration',
    'buildSettings': dict(base_settings),
    'name': 'Debug',
}
objects[ids['releaseCfg']] = {
    'isa': 'XCBuildConfiguration',
    'buildSettings': dict(base_settings),
    'name': 'Release',
}

objects[ids['configList']] = {
    'isa': 'XCConfigurationList',
    'buildConfigurations': [ids['debugCfg'], ids['releaseCfg']],
    'defaultConfigurationIsVisible': 0,
    'defaultConfigurationName': 'Release',
}

objects[ids['target']] = {
    'isa': 'PBXNativeTarget',
    'buildConfigurationList': ids['configList'],
    'buildPhases': [ids['sourcesPhase']],
    'buildRules': [],
    'dependencies': [],
    'name': PROJECT_NAME,
    'productName': PROJECT_NAME,
    'productReference': ids['productRef'],
    'productType': 'com.apple.product-type.application',
}

root = {
    'archiveVersion': 1,
    'classes': {},
    'objectVersion': 60,
    'objects': objects,
    'rootObject': ids['project'],
}

proj_dir = f'{PROJECT_NAME}.xcodeproj'
os.makedirs(proj_dir, exist_ok=True)
with open(os.path.join(proj_dir, 'project.pbxproj'), 'wb') as f:
    plistlib.dump(root, f, fmt=plistlib.FMT_XML)

# Workspace
ws_dir = f'{PROJECT_NAME}.xcworkspace'
os.makedirs(os.path.join(ws_dir), exist_ok=True)
with open(os.path.join(ws_dir, 'contents.xcworkspacedata'), 'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<Workspace>\n')
    f.write(f'  <FileRef location="container:{PROJECT_NAME}.xcodeproj"/>\n')
    f.write('</Workspace>\n')

print('done')
