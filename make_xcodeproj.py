#!/usr/bin/env python3
import os
import plistlib

PROJECT_NAME = "TromboneTuner"
SRC_DIR = "TromboneTuner"
SWIFT_FILES = [
    "TromboneTunerApp.swift",
    "ContentView.swift",
    "TunerViewModel.swift",
    "PitchDetector.swift",
    "Note.swift",
]

# Fixed IDs so scheme can reference them
OBJ_PROJECT = "A10000000000000000000001"
OBJ_MAIN_GROUP = "A10000000000000000000002"
OBJ_PRODUCTS_GROUP = "A10000000000000000000003"
OBJ_SOURCES_PHASE = "A10000000000000000000004"
OBJ_TARGET = "A10000000000000000000005"
OBJ_CONFIG_LIST = "A10000000000000000000006"
OBJ_DEBUG_CFG = "A10000000000000000000007"
OBJ_RELEASE_CFG = "A10000000000000000000008"
OBJ_PRODUCT_REF = "A10000000000000000000009"
FILE_IDS = [f"A100000000000000000010{i}" for i in range(len(SWIFT_FILES))]
BUILD_IDS = [f"A100000000000000000020{i}" for i in range(len(SWIFT_FILES))]

objects = {}
objects[OBJ_PROJECT] = {
    'isa': 'PBXProject',
    'attributes': {
        'LastUpgradeCheck': 1500,
        'TargetAttributes': {OBJ_TARGET: {'CreatedOnToolsVersion': '15.0'}}
    },
    'buildConfigurationList': OBJ_CONFIG_LIST,
    'compatibilityVersion': 'Xcode 15.0',
    'developmentRegion': 'en',
    'hasScannedForEncodings': 0,
    'knownRegions': ['en'],
    'mainGroup': OBJ_MAIN_GROUP,
    'productRefGroup': OBJ_PRODUCTS_GROUP,
    'projectDirPath': '',
    'projectRoot': '',
    'targets': [OBJ_TARGET],
}
objects[OBJ_PRODUCT_REF] = {
    'isa': 'PBXFileReference',
    'explicitFileType': 'wrapper.application',
    'includeInIndex': 0,
    'path': f'{PROJECT_NAME}.app',
    'sourceTree': 'BUILT_PRODUCTS_DIR',
}
objects[OBJ_PRODUCTS_GROUP] = {
    'isa': 'PBXGroup',
    'children': [OBJ_PRODUCT_REF],
    'name': 'Products',
    'sourceTree': '<group>',
}

children = []
builds = []
for i, fname in enumerate(SWIFT_FILES):
    objects[FILE_IDS[i]] = {
        'isa': 'PBXFileReference',
        'lastKnownFileType': 'sourcecode.swift',
        'name': fname,
        'path': f'{SRC_DIR}/{fname}',
        'sourceTree': '<group>',
    }
    children.append(FILE_IDS[i])
    objects[BUILD_IDS[i]] = {
        'isa': 'PBXBuildFile',
        'fileRef': FILE_IDS[i],
    }
    builds.append(BUILD_IDS[i])

objects[OBJ_MAIN_GROUP] = {
    'isa': 'PBXGroup',
    'children': children + [OBJ_PRODUCTS_GROUP],
    'sourceTree': '<group>',
}
objects[OBJ_SOURCES_PHASE] = {
    'isa': 'PBXSourcesBuildPhase',
    'buildActionMask': 2147483647,
    'files': builds,
    'runOnlyForDeploymentPostprocessing': 0,
}

base = {
    'CODE_SIGN_IDENTITY': '',
    'CODE_SIGNING_ALLOWED': 'NO',
    'CODE_SIGNING_REQUIRED': 'NO',
    'DEVELOPMENT_TEAM': '',
    'INFOPLIST_FILE': f'{SRC_DIR}/Info.plist',
    'IPHONEOS_DEPLOYMENT_TARGET': '16.0',
    'LD_RUNPATH_SEARCH_PATHS': ['$(inherited)', '@executable_path/Frameworks'],
    'PRODUCT_BUNDLE_IDENTIFIER': 'com.carte.trombonetuner',
    'PRODUCT_NAME': '$(TARGET_NAME)',
    'SDKROOT': 'iphoneos',
    'SUPPORTED_PLATFORMS': 'iphoneos iphonesimulator',
    'TARGETED_DEVICE_FAMILY': '1,2',
    'SWIFT_VERSION': '5.0',
    'ONLY_ACTIVE_ARCH': 'NO',
    'ARCHS': 'arm64',
}
objects[OBJ_DEBUG_CFG] = {'isa': 'XCBuildConfiguration', 'buildSettings': dict(base), 'name': 'Debug'}
objects[OBJ_RELEASE_CFG] = {'isa': 'XCBuildConfiguration', 'buildSettings': dict(base), 'name': 'Release'}
objects[OBJ_CONFIG_LIST] = {
    'isa': 'XCConfigurationList',
    'buildConfigurations': [OBJ_DEBUG_CFG, OBJ_RELEASE_CFG],
    'defaultConfigurationIsVisible': 0,
    'defaultConfigurationName': 'Release',
}
objects[OBJ_TARGET] = {
    'isa': 'PBXNativeTarget',
    'buildConfigurationList': OBJ_CONFIG_LIST,
    'buildPhases': [OBJ_SOURCES_PHASE],
    'buildRules': [],
    'dependencies': [],
    'name': PROJECT_NAME,
    'productName': PROJECT_NAME,
    'productReference': OBJ_PRODUCT_REF,
    'productType': 'com.apple.product-type.application',
}

root = {
    'archiveVersion': 1,
    'classes': {},
    'objectVersion': 56,
    'objects': objects,
    'rootObject': OBJ_PROJECT,
}

os.makedirs(f'{PROJECT_NAME}.xcodeproj', exist_ok=True)
with open(f'{PROJECT_NAME}.xcodeproj/project.pbxproj', 'wb') as f:
    plistlib.dump(root, f, fmt=plistlib.FMT_XML)

# Workspace
os.makedirs(f'{PROJECT_NAME}.xcworkspace', exist_ok=True)
with open(f'{PROJECT_NAME}.xcworkspace/contents.xcworkspacedata', 'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<Workspace>\n  <FileRef location="container:TromboneTuner.xcodeproj"/>\n</Workspace>\n')

# Scheme
os.makedirs(f'{PROJECT_NAME}.xcodeproj/xcshareddata/xcschemes', exist_ok=True)
scheme = f'''<?xml version="1.0" encoding="UTF-8"?>
<Scheme LastUpgradeVersion = "1500" version = "1.7">
  <BuildAction parallelizeBuildables = "YES" buildImplicitDependencies = "YES">
    <BuildActionEntries>
      <BuildActionEntry buildForTesting = "YES" buildForRunning = "YES" buildForProfiling = "YES" buildForArchiving = "YES" buildForAnalyzing = "YES">
        <BuildableReference BuildableIdentifier = "primary" BlueprintIdentifier = "{OBJ_TARGET}" BuildableName = "{PROJECT_NAME}.app" BlueprintName = "{PROJECT_NAME}" ReferencedContainer = "container:{PROJECT_NAME}.xcodeproj">
        </BuildableReference>
      </BuildActionEntry>
    </BuildActionEntries>
  </BuildAction>
  <TestAction buildConfiguration = "Debug" selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB" shouldUseLaunchSchemeArgsEnv = "YES"></TestAction>
  <LaunchAction buildConfiguration = "Debug" selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB" launchStyle = "0" useCustomWorkingDirectory = "NO" ignoresPersistentStateOnLaunch = "NO" debugDocumentVersioning = "YES" debugServiceExtension = "internal" allowLocationSimulation = "YES">
    <BuildableProductRunnable runnableDebuggingMode = "0">
      <BuildableReference BuildableIdentifier = "primary" BlueprintIdentifier = "{OBJ_TARGET}" BuildableName = "{PROJECT_NAME}.app" BlueprintName = "{PROJECT_NAME}" ReferencedContainer = "container:{PROJECT_NAME}.xcodeproj">
      </BuildableReference>
    </BuildableProductRunnable>
  </LaunchAction>
  <ProfileAction buildConfiguration = "Release" shouldUseLaunchSchemeArgsEnv = "YES" savedToolIdentifier = "" useCustomWorkingDirectory = "NO" debugDocumentVersioning = "YES">
    <BuildableProductRunnable runnableDebuggingMode = "0">
      <BuildableReference BuildableIdentifier = "primary" BlueprintIdentifier = "{OBJ_TARGET}" BuildableName = "{PROJECT_NAME}.app" BlueprintName = "{PROJECT_NAME}" ReferencedContainer = "container:{PROJECT_NAME}.xcodeproj">
      </BuildableReference>
    </BuildableProductRunnable>
  </ProfileAction>
  <AnalyzeAction buildConfiguration = "Debug"></AnalyzeAction>
  <ArchiveAction buildConfiguration = "Release" revealArchiveInOrganizer = "YES"></ArchiveAction>
</Scheme>
'''
with open(f'{PROJECT_NAME}.xcodeproj/xcshareddata/xcschemes/{PROJECT_NAME}.xcscheme', 'w') as f:
    f.write(scheme)

print('done')
