import os

def generate_hotspots_for_learning():
    """
    SonarCloudのSecurity Hotspotを意図的に発生させるための学習用関数
    """

    # ex1. password hard code
    db_password = "MySecretPassword123"
    print(f"Connecting with password: {db_password}")

    # ex2. command execute
    command = "ls -l"
    os.system(command)

    print("Hotspot generation test finished.")

if __name__ == "__main__":
    generate_hotspots_for_learning()
