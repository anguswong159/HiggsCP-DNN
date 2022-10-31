#!/bin/bash
#SBATCH --job-name=HiggsCPDNN         # Job name
#SBATCH --ntasks=1                    # Run on a single CPU
#SBATCH --gpus-per-node=1             # GPU
#SBATCH --mem=32gb                    # Job memory request
#SBATCH --time=08:00:00               # Time limit hrs:min:sec

python torch_model_rhorho_DNN.py -i /lustre/scratch/MCChu/angus/rhorho --no-label
