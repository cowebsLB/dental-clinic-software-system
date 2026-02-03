#!/usr/bin/env python
"""Development runner with auto-reload using hupper.

Usage:
    python run_dev.py
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path so 'main' module can be found
# This is needed for hupper's worker processes
script_dir = Path(__file__).parent.absolute()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Set working directory
os.chdir(script_dir)

if __name__ == "__main__":
    try:
        import hupper
        
        # Check if we're already running under hupper
        if hupper.is_active():
            # Already in reloader, just run main
            import main
            sys.exit(main.main())
        else:
            # Start the reloader - it will import and run main.main
            # The path is already set above, so worker processes should find it
            print("Starting with auto-reload enabled...")
            print("(Press Ctrl+C to stop)\n")
            reloader = hupper.start_reloader('main.main')
            
    except ImportError:
        print("Error: hupper is not installed.")
        print("Install it with: pip install hupper")
        print("\nFalling back to regular Python (no auto-reload)...")
        import main
        sys.exit(main.main())
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting hupper: {e}")
        print("\nFalling back to regular Python...")
        import main
        sys.exit(main.main())

