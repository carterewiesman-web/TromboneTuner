#!/usr/bin/env python3
"""Generate a valid Xcode project in the native ASCII plist format Xcode expects."""
import os

PROJECT_NAME = "TromboneTuner"
SRC_DIR = "TromboneTuner"
SWIFT_FILES = [
    "TromboneTunerApp.swift",
    "ContentView.swift",
    "TunerViewModel.swift",
    "PitchDetector.swift",
    "Note.swift",
]

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

def q(s):
    """Quote a string if it needs quoting."""
    if s == "" or any(c in s for c in ' \t\n"/$(){}[];=,:*@#!~`%^&|<>?'):
        return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return s

# Build sections
lines = []
lines.append("// !$*UTF8*$!")
lines.append("{")
lines.append("\tarchiveVersion = 1;")
lines.append("\tclasses = {")
lines.append("\t};")
lines.append("\tobjectVersion = 56;")
lines.append("\tobjects = {")

# PBXBuildFile section
lines.append("")
lines.append("/* Begin PBXBuildFile section */")
for i, fname in enumerate(SWIFT_FILES):
    lines.append(f"\t\t{BUILD_IDS[i]} /* {fname} in Sources */ = {{isa = PBXBuildFile; fileRef = {FILE_IDS[i]} /* {fname} */; }};")
lines.append("/* End PBXBuildFile section */")

# PBXFileReference section
lines.append("")
lines.append("/* Begin PBXFileReference section */")
lines.append(f"\t\t{OBJ_PRODUCT_REF} /* {PROJECT_NAME}.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = {PROJECT_NAME}.app; sourceTree = BUILT_PRODUCTS_DIR; }};")
for i, fname in enumerate(SWIFT_FILES):
    path = f"{SRC_DIR}/{fname}"
    lines.append(f"\t\t{FILE_IDS[i]} /* {fname} */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; name = {q(fname)}; path = {q(path)}; sourceTree = \"<group>\"; }};")
lines.append("/* End PBXFileReference section */")

# PBXGroup section
lines.append("")
lines.append("/* Begin PBXGroup section */")
children = " ".join(f"{fid} /* {fname} */," for fid, fname in zip(FILE_IDS, SWIFT_FILES))
lines.append(f"\t\t{OBJ_MAIN_GROUP} = {{")
lines.append("\t\t\tisa = PBXGroup;")
lines.append("\t\t\tchildren = (")
for fid, fname in zip(FILE_IDS, SWIFT_FILES):
    lines.append(f"\t\t\t\t{fid} /* {fname} */,")
lines.append(f"\t\t\t\t{OBJ_PRODUCTS_GROUP} /* Products */,")
lines.append("\t\t\t);")
lines.append("\t\t\tsourceTree = \"<group>\";")
lines.append("\t\t};")
lines.append(f"\t\t{OBJ_PRODUCTS_GROUP} /* Products */ = {{")
lines.append("\t\t\tisa = PBXGroup;")
lines.append("\t\t\tchildren = (")
lines.append(f"\t\t\t\t{OBJ_PRODUCT_REF} /* {PROJECT_NAME}.app */,")
lines.append("\t\t\t);")
lines.append("\t\t\tname = Products;")
lines.append("\t\t\tsourceTree = \"<group>\";")
lines.append("\t\t};")
lines.append("/* End PBXGroup section */")

# PBXNativeTarget section
lines.append("")
lines.append("/* Begin PBXNativeTarget section */")
lines.append(f"\t\t{OBJ_TARGET} /* {PROJECT_NAME} */ = {{")
lines.append("\t\t\tisa = PBXNativeTarget;")
lines.append(f"\t\t\tbuildConfigurationList = {OBJ_CONFIG_LIST} /* Build configuration list for PBXNativeTarget \"{PROJECT_NAME}\" */;")
lines.append("\t\t\tbuildPhases = (")
lines.append(f"\t\t\t\t{OBJ_SOURCES_PHASE} /* Sources */,")
lines.append("\t\t\t);")
lines.append("\t\t\tbuildRules = (")
lines.append("\t\t\t);")
lines.append("\t\t\tdependencies = (")
lines.append("\t\t\t);")
lines.append(f"\t\t\tname = {PROJECT_NAME};")
lines.append(f"\t\t\tproductName = {PROJECT_NAME};")
lines.append(f"\t\t\tproductReference = {OBJ_PRODUCT_REF} /* {PROJECT_NAME}.app */;")
lines.append("\t\t\tproductType = \"com.apple.product-type.application\";")
lines.append("\t\t};")
lines.append("/* End PBXNativeTarget section */")

# PBXProject section
lines.append("")
lines.append("/* Begin PBXProject section */")
lines.append(f"\t\t{OBJ_PROJECT} /* Project object */ = {{")
lines.append("\t\t\tisa = PBXProject;")
lines.append("\t\t\tattributes = {")
lines.append("\t\t\t\tBuildIndependentTargetsInParallel = 1;")
lines.append("\t\t\t\tLastUpgradeCheck = 1500;")
lines.append("\t\t\t\tTargetAttributes = {")
lines.append(f"\t\t\t\t\t{OBJ_TARGET} = {{")
lines.append("\t\t\t\t\t\tCreatedOnToolsVersion = 15.0;")
lines.append("\t\t\t\t\t};")
lines.append("\t\t\t\t};")
lines.append("\t\t\t};")
lines.append(f"\t\t\tbuildConfigurationList = {OBJ_CONFIG_LIST} /* Build configuration list for PBXProject \"{PROJECT_NAME}\" */;")
lines.append("\t\t\tcompatibilityVersion = \"Xcode 15.0\";")
lines.append("\t\t\tdevelopmentRegion = en;")
lines.append("\t\t\thasScannedForEncodings = 0;")
lines.append("\t\t\tknownRegions = (")
lines.append("\t\t\t\ten,")
lines.append("\t\t\t\tBase,")
lines.append("\t\t\t);")
lines.append(f"\t\t\tmainGroup = {OBJ_MAIN_GROUP};")
lines.append(f"\t\t\tproductRefGroup = {OBJ_PRODUCTS_GROUP} /* Products */;")
lines.append("\t\t\tprojectDirPath = \"\";")
lines.append("\t\t\tprojectRoot = \"\";")
lines.append("\t\t\ttargets = (")
lines.append(f"\t\t\t\t{OBJ_TARGET} /* {PROJECT_NAME} */,")
lines.append("\t\t\t);")
lines.append("\t\t};")
lines.append("/* End PBXProject section */")

# PBXSourcesBuildPhase section
lines.append("")
lines.append("/* Begin PBXSourcesBuildPhase section */")
lines.append(f"\t\t{OBJ_SOURCES_PHASE} /* Sources */ = {{")
lines.append("\t\t\tisa = PBXSourcesBuildPhase;")
lines.append("\t\t\tbuildActionMask = 2147483647;")
lines.append("\t\t\tfiles = (")
for bid, fname in zip(BUILD_IDS, SWIFT_FILES):
    lines.append(f"\t\t\t\t{bid} /* {fname} in Sources */,")
lines.append("\t\t\t);")
lines.append("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
lines.append("\t\t};")
lines.append("/* End PBXSourcesBuildPhase section */")

# XCBuildConfiguration section
lines.append("")
lines.append("/* Begin XCBuildConfiguration section */")
def build_cfg(cfg_id, name):
    out = []
    out.append(f"\t\t{cfg_id} /* {name} */ = {{")
    out.append("\t\t\tisa = XCBuildConfiguration;")
    out.append("\t\t\tbuildSettings = {")
    out.append("\t\t\t\tARCHS = arm64;")
    out.append("\t\t\t\tCODE_SIGN_IDENTITY = \"\";")
    out.append("\t\t\t\tCODE_SIGNING_ALLOWED = NO;")
    out.append("\t\t\t\tCODE_SIGNING_REQUIRED = NO;")
    out.append("\t\t\t\tDEVELOPMENT_TEAM = \"\";")
    out.append(f"\t\t\t\tINFOPLIST_FILE = {SRC_DIR}/Info.plist;")
    out.append("\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 16.0;")
    out.append("\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (")
    out.append("\t\t\t\t\t\"$(inherited)\",")
    out.append("\t\t\t\t\t\"@executable_path/Frameworks\",")
    out.append("\t\t\t\t);")
    out.append("\t\t\t\tONLY_ACTIVE_ARCH = NO;")
    out.append(f"\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = com.carte.trombonetuner;")
    out.append("\t\t\t\tPRODUCT_NAME = \"$(TARGET_NAME)\";")
    out.append("\t\t\t\tSDKROOT = iphoneos;")
    out.append("\t\t\t\tSUPPORTED_PLATFORMS = \"iphoneos iphonesimulator\";")
    out.append("\t\t\t\tSWIFT_VERSION = 5.0;")
    out.append("\t\t\t\tTARGETED_DEVICE_FAMILY = \"1,2\";")
    out.append("\t\t\t};")
    out.append(f"\t\t\tname = {name};")
    out.append("\t\t};")
    return out

lines.extend(build_cfg(OBJ_DEBUG_CFG, "Debug"))
lines.extend(build_cfg(OBJ_RELEASE_CFG, "Release"))
lines.append("/* End XCBuildConfiguration section */")

# XCConfigurationList section
lines.append("")
lines.append("/* Begin XCConfigurationList section */")
lines.append(f"\t\t{OBJ_CONFIG_LIST} /* Build configuration list for PBXProject \"{PROJECT_NAME}\" */ = {{")
lines.append("\t\t\tisa = XCConfigurationList;")
lines.append("\t\t\tbuildConfigurations = (")
lines.append(f"\t\t\t\t{OBJ_DEBUG_CFG} /* Debug */,")
lines.append(f"\t\t\t\t{OBJ_RELEASE_CFG} /* Release */,")
lines.append("\t\t\t);")
lines.append("\t\t\tdefaultConfigurationIsVisible = 0;")
lines.append("\t\t\tdefaultConfigurationName = Release;")
lines.append("\t\t};")
lines.append("/* End XCConfigurationList section */")

lines.append("\t};")
lines.append(f"\trootObject = {OBJ_PROJECT} /* Project object */;")
lines.append("}")

# Write pbxproj
os.makedirs(f"{PROJECT_NAME}.xcodeproj", exist_ok=True)
with open(f"{PROJECT_NAME}.xcodeproj/project.pbxproj", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

# Workspace
os.makedirs(f"{PROJECT_NAME}.xcworkspace", exist_ok=True)
with open(f"{PROJECT_NAME}.xcworkspace/contents.xcworkspacedata", "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<Workspace>\n  <FileRef location="container:TromboneTuner.xcodeproj"/>\n</Workspace>\n')

# Scheme
os.makedirs(f"{PROJECT_NAME}.xcodeproj/xcshareddata/xcschemes", exist_ok=True)
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
with open(f"{PROJECT_NAME}.xcodeproj/xcshareddata/xcschemes/{PROJECT_NAME}.xcscheme", "w") as f:
    f.write(scheme)

print("done")
