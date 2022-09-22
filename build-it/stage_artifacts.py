import argparse
import logging
import os
from pathlib import Path
import sys
import tarfile
from zipfile import ZipFile

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
_logger.addHandler(handler)

def main():
    args = parse_args()
    stage_artifacts_for_export(args.downloaded_path, args.stageing_path)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Parsing the script parameters"
    )
    parser.add_argument(
        "--downloaded_path",
        help="artifact downloaded path",
        default="",
    )
    parser.add_argument(
        "--staging_path",
        help="Artifact staging directory",
        default=""
    )
    _logger.debug(f"The parameters for the script are: {parser.parse_args()}")
    return parser.parse_args()

def stage_artifacts_for_export(artifact_paths, working_directory):
    tar_staging_directory = prepare_directory(working_directory, "Tar_Staging_Directory")
    for artifact_path in artifact_paths:
        unzip_artifact(artifact_path, tar_staging_directory)
    stage_artifacts(working_directory, tar_staging_directory)

def prepare_directory(working_directory, sub_directory):
    new_directory = Path(working_directory) / sub_directory
    if not os.path.exists(new_directory):
        os.makedirs(new_directory, exist_ok=True)
    return new_directory

def unzip_artifact(artifact_path, tar_staging_directory):
    with ZipFile(artifact_path) as z:
        if len(z.namelist()) == 1 and z.namelist()[0].endswith("tar.gz"):
            z.extractall(path=Path(tar_staging_directory))
        _logger.debug(f"Unzipped {z.namelist()[0]}")

def stage_artifacts(working_directory, tar_staging_directory):
    tar_artifacts = os.listdir(tar_staging_directory)
    top_level_dll_directory = prepare_directory(working_directory, sub_directory="TopLevelDlls")
    for tar_artifact in tar_artifacts:
        extract_tarfile(tar_artifact, tar_staging_directory, top_level_dll_directory)

def extract_tarfile(tar_file_name, staging_directory, top_level_dll_directory):
    _logger.debug(f"Creating folder Heirarchy for Server Dlls...")
    _logger.debug(f"extracing tar file {tar_file_name}...")
    with tarfile.open(Path(staging_directory) / tar_file_name) as tar_file:
        for artifact in tar_file.getmembers():
            if(tar_file_name.find('x64') != -1):
                bitness_type = 'Win64'
            elif(tar_file_name.find('x86') != -1):
                bitness_type = 'Win32'
            elif(tar_file_name.find('linux') != -1):
                bitness_type = 'Linux'
            elif(tar_file_name.find('rt') != -1):
                bitness_type = 'LinuxRT'
            extract_and_stage_artifact(artifact, tar_file, bitness_type, top_level_dll_directory)
        _logger.debug(f"extracted {tar_file.getnames()} to {staging_directory}")

def extract_and_stage_artifact(artifact, tar_file, bitness_type, top_level_dll_directory):
    server_folder = prepare_directory(top_level_dll_directory, sub_directory="LabVIEW gRPC Server")
    generator_folder = prepare_directory(top_level_dll_directory, sub_directory="LabVIEW gRPC Generator")
    if(artifact.name.find('server') != -1 ):
        extract_directory = (Path(server_folder) / bitness_type)
    elif(artifact.name.find('generator') != -1):
        extract_directory = (Path(generator_folder) / bitness_type)
    os.makedirs(extract_directory, exist_ok=True)
    tar_file.extract(artifact, extract_directory)

if __name__ == "__main__":
    main()