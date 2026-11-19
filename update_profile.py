"""Compatibility entry point for the original hourly profile refresh."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'scripts'))
from refresh_profile import main
if __name__=='__main__':main()
