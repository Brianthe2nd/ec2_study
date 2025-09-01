import os
import shutil
import zipfile
from datetime import datetime
import uuid

def collect_and_zip_files(folder_path):
    """
    Collect all .txt, .csv, and .json files from a given folder,
    copy them into a new subfolder with a unique name, and zip that folder.
    """
    unique_id = uuid.uuid4().hex[:6]  # short random ID
    folder_name = f"collected_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{unique_id}"
    temp_folder = os.path.join(folder_path, folder_name)
    os.makedirs(temp_folder, exist_ok=True)

    # File extensions we care about
    extensions = (".txt", ".csv", ".json")

    # Copy matching files into temp folder
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if file.endswith(extensions) and os.path.isfile(file_path):
            shutil.copy(file_path, temp_folder)

    # Create zip file (zip goes next to original folder, not inside temp)
    zip_name = f"{folder_name}.zip"
    zip_path = os.path.join(folder_path, zip_name)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_folder)  # relative path inside zip
                zipf.write(file_path, arcname)

    print(f"✅ Collected files from: {folder_path}")
    print(f"✅ Zipped archive created: {zip_path}")

    return temp_folder, zip_path


if __name__ == "__main__":
    cwd = os.getcwd()
    archive_folder = os.path.join(cwd, "archive")
    os.makedirs(archive_folder, exist_ok=True)

    zipped_files = []

    # Process each subfolder inside cwd
    for item in os.listdir(cwd):
        folder_path = os.path.join(cwd, item)
        if os.path.isdir(folder_path) and item != "archive":
            temp_folder, zip_path = collect_and_zip_files(folder_path)
            zipped_files.append(zip_path)

    # Move all zipped files into archive
    for zipped_file in zipped_files:
        dest = os.path.join(archive_folder, os.path.basename(zipped_file))
        shutil.move(zipped_file, dest)
        print(f"📦 Moved {zipped_file} -> {dest}")
