#!/bin/bash
cd fpga_wand/Information-Processing_Group_10_fpga_wand/cloud/backend/brain/
source .venv/bin/activate
cd ~/fpga_wand/Information-Processing_Group_10_fpga_wand/cloud
export DATABASE_URL=postgresql://wanduser:strongpassword@localhost/fpgawand
uvicorn main:app --host 0.0.0.0 --port 8000