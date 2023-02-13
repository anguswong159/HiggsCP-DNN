#!/bin/bash
#SBATCH --job-name=HiggsCPDNN_no_label         # Job name
#SBATCH --ntasks=1                    # Run on a single CPU
#SBATCH --gres=gpu:1                  # GPU
#SBATCH --mem=32gb                    # Job memory request
#SBATCH --time=02:00:00               # Time limit hrs:min:sec

python torch_model_rhorho_DNN_collin_approx.py -i /lustre/scratch/MCChu/angus/rhorho_collin_reject_n_no_label --z_fraction 1 --num_classes 11 --hep_coord -f Collin-approx --no-label
