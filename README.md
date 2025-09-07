# On the Constancy of Latency at the Internet's Edge

Thank you for your interest in our work!

This repository will contain the code and data associated with our paper. We are in the process of organizing and uploading all materials, and everything will be made available shortly.

Please check back soon, and feel free to reach out if you have any questions in the meantime.

- By Aditya, Vaibhav, Aniket, Bala, and Vinayak
- Email: f20212071@goa.bits-pilani.ac.in OR adityabhat2003@yahoo.com

## Overview
 
The technical paper "On the Constancy of Latency at the Internet's Edge" presented at TMA Conference 2025 is available [here](https://tma.ifip.org/2025/wp-content/uploads/sites/14/2025/06/tma2025_paper10.pdf)

## Data

`data/raw`: contains 400 raw measurement data JSON files that we collected using RIPE Atlas. The `N` in `data/raw/measurement_N_results.json` is the unique measurement ID assigned by RIPE Atlas to this measurement. Please refer to our paper for more details.

Work in progress...

## Installation

It is recommended to use a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Then install the required packages:

```bash
pip install -r requirements.txt
```
You also need to follow the installation in https://github.com/SmartMonitoringSchemes/HDPHMM.jl/tree/master to use the HMM-HDP method.

## Usage

Work in progress...

## Citation

If you use this code or data in your work, please cite:

```
@inproceedings{bhat2025constancy,
  author    = {Aditya Bhat and Vaibhav Ganatra and Aniket Shaha and Balakrishnan Chandrasekaran and Vinayak Naik},
  title     = {On the Constancy of Latency at the Internet’s Edge},
  booktitle = {Proceedings of the International Conference on Traffic Monitoring and Analysis (TMA)},
  year      = {2025},
  month     = {June}
}
```
