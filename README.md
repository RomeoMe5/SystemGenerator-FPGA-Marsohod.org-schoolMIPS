FPGAMarsohod System Generator
===============
CAD for generating base configurations (system generator) for FPGA development boards from "Marsohod.org" (Марсоход2, Марсоход3, Марсоход2bis, Марсоход3bis, et. al).   
Demo:     
https://fpga-marsohod-generator.herokuapp.com/    
    
Structure:
* `engine` - core logic of generating FPGA Quartus-compatible configurations.
* `api_client.py` - simple rest-like API.
* `cli_client.py` - simple cli client. Engine could also be used directly as python package (see `engine_example.py` form `examples` folder).
* `web_client.py` - base web interface for solution. Written with legacy bootstrap and flask. TODO: should be overwritten as SPA with API usage.

### Requirements
* Python >= 3.9

### How to run
See `run.sh`.
