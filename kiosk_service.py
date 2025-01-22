# main.py
import time
import sys

import arcus
#import fme

if __name__ == "__main__":
    # 1. Initialize Arcus
    arcus_ok = arcus.init_arcus()

    # 2. Initialize FME, if using
    # fme_ok = fme.init_fme()

    if not arcus_ok:
        print("Arcus init failed. Exiting.")
        sys.exit(1)
    # if not fme_ok:
    #     print("FME init failed. Exiting.")
    #     sys.exit(1)

    print("Arcus device initialized successfully.")

    # Keep running or do more logic
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")

    # Close everything on exit
    arcus.close_arcus()
    # fme.close_fme()
    print("Exited cleanly.")
