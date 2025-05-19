import os, subprocess, pathlib, signal

def start_s3_proc():
    # Check that s3/bin/s3manager exists
    print("Checking for s3/bin/s3manager")
    if not pathlib.Path("s3/bin/s3manager").exists():
        raise RuntimeError("s3/bin/s3manager executable not found. Download from https://github.com/cloudlena/s3manager")

    env = os.environ.copy()

    env["PORT"] = "5000"
    env["ACCESS_KEY_ID"] = os.environ["AWS_ACCESS_KEY_ID"]
    env["SECRET_ACCESS_KEY"] = os.environ["AWS_SECRET_ACCESS_KEY"]
    env["ENDPOINT"] = os.environ["AWS_ENDPOINT_URL"].split("://")[1]
    if os.environ["AWS_ENDPOINT_URL"].split("://")[0] == "http":
        env["USE_SSL"] = "false"
    else:
        env["USE_SSL"] = "true"

    print(env["ENDPOINT"])

    while True:
        try:
            subprocess.check_call(["s3/bin/s3manager"], env=env, shell=True)
        except subprocess.CalledProcessError as e:
            if e.returncode == -signal.SIGINT or e.returncode == -signal.SIGILL or e.returncode == -signal.SIGQUIT:
                print("Reached error code, shutting down...")
                return

            print(f"Got error in s3_proc: {e} with code {e.returncode}")