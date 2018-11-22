import zipfile
import os

if __name__ == '__main__':
    instances_dir = "instances"
    python_files_to_package = ["__main__.py", "heuristics.py", "IOmanager.py", "method_runner.py",
                        "options.py", "scheduler.py", "validator.py"]
    instances_files_to_package = [os.path.join(instances_dir, x) for x in os.listdir(instances_dir)]
    with zipfile.ZipFile('inf127083.zip', 'w') as zip_file:
        [zip_file.write(x) for x in python_files_to_package]
        [zip_file.write(x) for x in instances_files_to_package]
