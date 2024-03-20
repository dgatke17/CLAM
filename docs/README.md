CLAM <img src="clam-logo.png" width="280px" align="right" />
===========
CLAM repository for the 4th semester of the MSc in Biomedical Engineering


# 1. Setup

Start med at clone CLAM repository fra [https://github.com/mahmoodlab/CLAM/](https://github.com/mahmoodlab/CLAM/blob/master/docs/INSTALLATION.md) til den ønskede mappe

```bash
git clone https://github.com/mahmoodlab/CLAM.git
```

Lav et nyt conda environment til CLAM

```bash
conda env export --no-builds > docs/clam.yaml
conda env create -f docs/clam.yaml -n clam
```

Aktivér det nye environment

```bash
conda activate clam
```

Installér openslide-python

```bash
pip install openslide-python
```

Fix nødvendige imports

```bash
# add 'requirements.txt' to clam directory (i.e. ~/clam/)
pip install -r ~/CLAM/requirements.txt
```

[requirements.txt](https://prod-files-secure.s3.us-west-2.amazonaws.com/ee206058-e5a1-4ae2-a7b4-83939dbeccd3/f1a15d69-b8bd-45e3-ad0f-e41d5f9254ae/requirements.txt)

Installér openslide

```bash
conda config --append channels conda-forge
conda install openslide
```

Installér smooth-topk i en mappe udenfor CLAM mappen

```bash
git clone https://github.com/oval-group/smooth-topk.git
cd smooth-topk
python setup.py install
```

Her i processen sker der noget møgirriterende, da vi ikke har ’super-user’ privilegier og derfor ikke kan installere de nødvendige imports. Det kræver en workaround, hvor man laver en writable sandbox af sit container image og installerer de sidste imports heri:

```bash
# det her er det eneste der virker, har bare ikke skrevet det ind her endnu.
# fuck alt det med anaconda.. sandbox'en er det eneste der fungerer
```

# 2. Segmentering af tissue

Opret en mappe (skal kaldes DATA_DIRECTORY) der skal holde billederne

```bash
DATA_DIRECTORY/
	├── slide_1.tiff
	├── slide_2.tiff
	└── ...
```

Samme for RESULTS_DIRECTORY med tre tilhørende sub-folders (masks, patches, stitches)

```bash
RESULTS_DIRECTORY/
	├── masks
    		├── slide_1.png
    		├── slide_2.png
    		└── ...
	├── patches
    		├── slide_1.h5
    		├── slide_2.h5
    		└── ...
	├── stitches
    		├── slide_1.png
    		├── slide_2.png
    		└── ...
```

cd til CLAM mappen og kør segmentering

```bash
cd CLAM
python create_patches_fp.py
```

# 3. Feature extraction

Opret følgende to mapper 

```bash
CLAM/
	├── DIR_TO_COORDS
	├── FEATURES_DIRECTORY
```

Gå til mappen “dataset_csv” og ændr IDs og label for den ønskede task(binary/subtyping), så det passer til vores data. Fx:

```bash
# .csv example

case_id,slide_id,label
patient_1,normal_001,normal_tissue
patient_2,normal_002,tumor_tissue
patient_3,normal_003,normal_tissue
```

Åbn “extract_features_fp.py” og ændr argumenterne til parser, så de passer til vores directories og den korrekte extension på data (.tif)

```python
parser = argparse.ArgumentParser(description='Feature Extraction')
parser.add_argument('--data_h5_dir', type=str, default='DIR_TO_COORDS')
parser.add_argument('--data_slide_dir', type=str, default='DATA_DIRECTORY')
parser.add_argument('--slide_ext', type=str, default= '.tif')
parser.add_argument('--csv_path', type=str, default='dataset_csv/tumor_vs_normal_dummy_clean.csv')
parser.add_argument('--feat_dir', type=str, default='FEATURES_DIRECTORY')
parser.add_argument('--batch_size', type=int, default=256)
parser.add_argument('--no_auto_skip', default=False, action='store_true')
parser.add_argument('--custom_downsample', type=int, default=1)
parser.add_argument('--target_patch_size', type=int, default=-1)
args = parser.parse_args()
```

Udfør feature extraction ved at køre “extract_features_fp.py” i terminal

```bash
cd CLAM
python extract_features_fp.py
```

# 4. Forbered feature data til training

Opret følgende directories og overfør extracted features i FEATURES_DIRECTORY til de korrekte directories. Alt efter hvor mange dataset vi bruger, skal der oprettes flere undermapper (DATASET_1_DATA_DIR, DATASET_2_DATA_DIR…)

```bash
DATA_ROOT_DIR/
    ├──DATASET_1_DATA_DIR/
        ├── h5_files
                ├── slide_1.h5
                ├── slide_2.h5
                └── ...
        └── pt_files
                ├── slide_1.pt
                ├── slide_2.pt
                └── ...
    ├──DATASET_2_DATA_DIR/
        ├── h5_files
                ├── slide_a.h5
                ├── slide_b.h5
                └── ...
        └── pt_files
                ├── slide_a.pt
                ├── slide_b.pt
                └── ...
    └──DATASET_3_DATA_DIR/
        ├── h5_files
                ├── slide_i.h5
                ├── slide_ii.h5
                └── ...
        └── pt_files
                ├── slide_i.pt
                ├── slide_ii.pt
                └── ...
    └── ...
```

# 5. Training

Åbn “create_splits_seq.py”. Start med at splitte data i det ønskede split ved at ændre parser argumenterne og stien til vores .csv fil over data

```bash
# fx skal følgende udsnit af koden ændres til dette:

parser.add_argument('--task', type=str, choices=['task_1_tumor_vs_normal','task_2_tumor_subtyping'], default='task_1_tumor_vs_normal') # for the binary task

dataset = Generic_WSI_Classification_Dataset(csv_path = 'dataset_csv/<file_name>.csv',

# derudover kan split ændres deri
```

Split derefter data ved at køre følgende i terminal

```bash
cd CLAM
python create_splits_seq.py
```

Efter at have splittet data, så kan training begynde. Training startes fra “main.py”. Først skal alle parametre og de forskellige stier indstilles i parser argumenterne

 

```bash
# main.py 
# fx linjerne:

parser.add_argument('--task', type=str, choices=['task_1_tumor_vs_normal',  'task_2_tumor_subtyping'], default='task_1_tumor_vs_normal')

parser.add_argument('--split_dir', type=str, default='splits/task_1_tumor_vs_normal_100', 

parser.add_argument('--data_root_dir', type=str, default='DATA_ROOT_DIR',

# derudover kan der ændres på andre parametre for træningen, så som epochs, loss function, learning rate, osv..
```

Længere nede i koden i “main.py” findes følgende kode. Vær sikker på, at der henvises til den korrekte .csv fil over vores data og den rigtige path til vores dataset (DATASET_1_DATA_DIR)

```python
if args.task == 'task_1_tumor_vs_normal':
    args.n_classes=2
    dataset = Generic_MIL_Dataset(csv_path = 'dataset_csv/tumor_vs_normal_dummy_clean.csv',
                            data_dir= os.path.join(args.data_root_dir, 'DATASET_1_DATA_DIR'),
                            shuffle = False, 
                            seed = args.seed, 
                            print_info = True,
                            label_dict = {'normal_tissue':0, 'tumor_tissue':1},
                            patient_strat=False,
                            ignore=[])
```

Efter at have specificeret parametre og angivet de korrekte paths til vores directories, kan training startes

```bash
cd CLAM
python main.py
```

Man kan følge training I real-time ved at køre følgende i terminal:

```bash
srun singularity shell --writable --fakeroot pytorch-24.02

tensorboard --logdir=master/test2/CLAM/
```

# 6. Testing and evaluation

Meget simpelt at teste. Åbn “eval.py” og ændr de nødvendige parser arguments og de korrekte paths til directories og .csv fil. Herefter køres “eval.py”

```bash
cd CLAM
python eval.py
```

# 7. Heatmap visualisation

Visualisering af feature heatmaps kan blive lavet ved at køre “create_heatmaps.py”. 

```bash
cd CLAM
python create_heatmaps.py
```

# AI Cloud implementation

## 1. Singularity setup

```bash
# download latest PyTorch singularity container (24.02 as of now)

srun --mem 64G singularity pull docker://nvcr.io/nvidia/pytorch:24.02-py3

```

```bash
# run and open the downloaded singularity container

srun --pty singularity shell pytorch_24.02-py3.sif
```

## 2. Conda setup

```bash
# retrieve the latest linux version of conda from the conda repository

wget https://repo.anaconda.com/archive/Anaconda3-2024.02-1-Linux-x86_64.sh --no-check-certificate
```

```bash
# install the downloaded conda shell and agree to the 'end user license agreement'

bash ~/Anaconda3-2024.02-1-Linux-x86_64.sh
```

## 3. Perform steps 1-7 of the CLAM installation

```bash
# when in your singularity, open conda by the following command and then perform steps 1-7

source ~/anaconda3/bin/activate
```

