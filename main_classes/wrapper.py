#!/usr/bin/env python
# coding: utf-8

############## PART 1: IMPORT STATEMENTS ##############

# import system libraries
import shutil
from datetime import datetime
from subprocess import call
import warnings
warnings.filterwarnings("ignore")
import logging

# import core functions
from generic_automl_classes import * # need all packages defined here
from generic_autokeras import AutoKerasClassification, AutoKerasRegression 
from generic_deepswarm import DeepSwarmClassification, DeepSwarmRegression
from generic_tpot import TPOTClassification, TPOTRegression 

# enable multiprocessing in Forkserver mode
import multiprocessing
multiprocessing.set_start_method('forkserver')

############## PART 2: HELPER FUNCTIONS ##############

def copy_full_dir(source, target):
    """helper function to copy directory for backups
    Parameters
    ----------
    source : dir to be copied
    target : location of copy destination 
    
    Returns
    -------
    None
    """ 

    call(['cp', '-a', source, target]) # Unix

############## PART 3: FUNCTIONS TO RUN BINARY CLASSIFICATION, MULTI-CLASS CLASSIFICATION, REGRESSION ##############

def run_binaryclass(data_folder, data_file, sequence_type, model_folder, output_folder, automl_search_techniques, max_runtime_minutes, num_folds, verbosity, do_backup, do_auto_bin, bin_threshold, input_col, target_col, pad_seqs, augment_data, dataset_robustness, num_final_epochs, yaml_params, num_generations, population_size, run_interpretation, interpret_params, run_design, design_params):
    """run all three AutoML modules for binary classification
    Parameters
    ----------
    data_folder : str representing folder where data is stored
    data_file : str representing file name where data is stored
    sequence_type : str, either 'nucleic_acid', 'peptide', or 'glycan'
    model_folder : str representing folder where models are to be stored
    output_folder : str representing folder where output is to be stored
    automl_search_techniques : str representing which AutoML search technique should be performed, one of 'all', 'deepswarm', 'autokeras', 'tpot'
    max_runtime_minutes : int representing max runtime for model search in minutes
    num_folds : int representing num folds
    verbosity : int representing 0=not verbose, 1=verbose
    do_backup : bool representing if a backup should be performed
    do_auto_bin : bool representing if target values should be automatically binned
    bin_threshold : float representing threshold for positive and negative classes
    input_col : str representing input column name where sequences can be located
    target_col : str representing target column name where target values can be located
    pad_seqs : str indicating pad_seqs method, either 'max', 'min', 'average'
    augment_data : str, either 'none', 'complement', 'reverse_complement', or 'both_complements'
    dataset_robustness : bool indicating if data ablation study should be performed
    num_final_epochs : int representing number of final epochs to train final deepswarm model
    yaml_params : dict of extra deepswarm parameters, with keys 'max_depth' (int), 'ant_count' (int), 'epochs' (int)
    num_generations : int representing number of generations of tpot search
    population_size : int representing population size of tpot search
    run_interpretation : bool indicating if interpretation module should be executed
    interpret_params : dict of extra interpretation parameters, with keys 'sample_number_class_activation_maps' (int), 'class_activation_grad_modifier' (str), 'class_activation_layer_index' (int);
        'sample_number_saliency_maps' (int), 'saliency_map_grad_modifier' (str), 'saliency_map_layer_index' (int), 'sample_number_mutagenesis' (int)
    run_design : bool indicating if design module should be executed
    design_params :dict of extra design parameters, with keys 'k' (int), 'substitution_type' (str), 'target_y' (float), 'class_of_interest' (int), 'constraint_file_path' (str);
        'de_novo_num_seqs_to_test' (int), 'storm_num_seqs_to_test' (int), 'num_of_optimization_rounds' (int)
    
    Returns
    -------
    None
    """ 

    data_path = data_folder + data_file 

    if automl_search_techniques == 'all' or automl_search_techniques == 'deepswarm':  
        print("#################################################################################################")
        print("##############################            RUNNING DEEPSWARM           ###########################")
        print("#################################################################################################")

        # DeepSwarm AutoML method based on: 
        #      Byla, E. and Pang, W., 2019. DeepSwarm: Optimising Convolutional 
        #      Neural Networks using Swarm Intelligence. arXiv preprint arXiv:1905.07350.
        #   Script adapted from:
        #      https://github.com/Pattio/DeepSwarm

        # define run folder path to store generated models and data
        run_folder = 'deepswarm/binary_classification/'

        # refresh model folder
        if not os.path.isdir(model_folder + run_folder):
            os.mkdir(model_folder + run_folder)

        # refresh outputs folder
        if not os.path.isdir(output_folder + run_folder):
            os.mkdir(output_folder + run_folder)

        dsc = DeepSwarmClassification(data_path, model_folder + run_folder, output_folder + run_folder, max_runtime=max_runtime_minutes, num_folds=num_folds, sequence_type=sequence_type, do_auto_bin=do_auto_bin, bin_threshold=bin_threshold, verbosity=verbosity, yaml_params=yaml_params, num_final_epochs=num_final_epochs, input_col=input_col, target_col=target_col, pad_seqs=pad_seqs, augment_data=augment_data, multiclass=False, dataset_robustness=dataset_robustness, run_interpretation = run_interpretation, interpret_params = interpret_params, run_design = run_design, design_params = design_params)
        dsc.run_system()

        # create backup folder
        if do_backup:
            backup_folder = './backup/runs/' +  datetime.now().strftime('%Y%m%d') + '/' + run_folder
            # create folder to store model (if not existent)
            if not os.path.isdir(backup_folder):
                os.makedirs(backup_folder)

            # copy all contents to dated backup
            copy_full_dir(model_folder + run_folder, backup_folder + model_folder[2:])
            copy_full_dir(output_folder + run_folder, backup_folder + output_folder[2:])
    
    if automl_search_techniques == 'all' or automl_search_techniques == 'autokeras': 

        print("#################################################################################################")
        print("##############################            RUNNING AUTOKERAS           ###########################")
        print("#################################################################################################")
        
        # AutoKeras AutoML method based on: 
        #      Jin, H., Song, Q. and Hu, X., 2019, July. Auto-keras: An efficient neural architecture search system. 
        #      In Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & 
        #      Data Mining (pp. 1946-1956). ACM.
        #   Script adapted from:
        #      https://github.com/keras-team/autokeras

        # define run folder path to store generated models and data
        run_folder = 'autokeras/binary_classification/'

        # refresh model folder
        if not os.path.isdir(model_folder + run_folder):
            os.mkdir(model_folder + run_folder)

        # refresh outputs folder
        if not os.path.isdir(output_folder + run_folder):
            os.mkdir(output_folder + run_folder)

        # autokeras execution
        akc = AutoKerasClassification(data_path, model_folder + run_folder, output_folder + run_folder, max_runtime=max_runtime_minutes, num_folds=num_folds, sequence_type=sequence_type, do_auto_bin=do_auto_bin, bin_threshold=bin_threshold, verbosity=verbosity, input_col=input_col, target_col=target_col, pad_seqs=pad_seqs, augment_data=augment_data, multiclass=False, dataset_robustness=dataset_robustness, run_interpretation = run_interpretation, interpret_params = interpret_params, run_design = run_design, design_params = design_params)
        akc.run_system()

        # create backup folder
        if do_backup:
            backup_folder = './backup/runs/' +  datetime.now().strftime('%Y%m%d') + '/' + run_folder
            # create folder to store model (if not existent)
            if not os.path.isdir(backup_folder):
                os.makedirs(backup_folder)

            # copy all contents to dated backup
            copy_full_dir(model_folder + run_folder, backup_folder + model_folder[2:])
            copy_full_dir(output_folder + run_folder, backup_folder + output_folder[2:])

    if automl_search_techniques == 'all' or automl_search_techniques == 'tpot': 

        print("#################################################################################################")
        print("##############################            RUNNING TPOT                ###########################")
        print("#################################################################################################")

        # TPOT AutoML method based on: 
        #      Olson, R.S., Bartley, N., Urbanowicz, R.J. and Moore, J.H., 2016, July. Evaluation of a tree-based 
        #      pipeline optimization tool for automating data science. In Proceedings of the Genetic and Evolutionary 
        #      Computation Conference 2016 (pp. 485-492). ACM.
        #   Script adapted from:
        #      https://github.com/EpistasisLab/tpot

        # define run folder path to store generated models and data
        run_folder = 'tpot/binary_classification/'

        # refresh model folder
        if not os.path.isdir(model_folder + run_folder):
            os.mkdir(model_folder + run_folder)

        # refresh outputs folder
        if not os.path.isdir(output_folder + run_folder):
            os.mkdir(output_folder + run_folder)

        tpc = TPOTClassification(data_path, model_folder + run_folder, output_folder + run_folder, max_runtime=max_runtime_minutes, num_folds=num_folds, sequence_type=sequence_type, do_auto_bin=do_auto_bin, bin_threshold=bin_threshold, verbosity=verbosity, population_size=population_size, num_generations=num_generations, input_col=input_col, target_col=target_col, pad_seqs=pad_seqs, augment_data=augment_data, multiclass=False, dataset_robustness=dataset_robustness, run_interpretation = run_interpretation, interpret_params = interpret_params, run_design = run_design, design_params = design_params)
        tpc.run_system()

        # create backup folder
        if do_backup:
            backup_folder = './backup/runs/' +  datetime.now().strftime('%Y%m%d') + '/' + run_folder
            # create folder to store model (if not existent)
            if not os.path.isdir(backup_folder):
                os.makedirs(backup_folder)

            # copy all contents to dated backup
            copy_full_dir(model_folder + run_folder, backup_folder + model_folder[2:])
            copy_full_dir(output_folder + run_folder, backup_folder + output_folder[2:])

def run_multiclass(data_folder, data_file, sequence_type, model_folder, output_folder, automl_search_techniques, max_runtime_minutes, num_folds, verbosity, do_backup, do_auto_bin, bin_threshold, input_col, target_col, pad_seqs, augment_data, dataset_robustness, num_final_epochs, yaml_params, num_generations, population_size, run_interpretation, interpret_params, run_design, design_params):
    """run all three AutoML modules for multi-class classification
    Parameters
    ----------
    data_folder : str representing folder where data is stored
    data_file : str representing file name where data is stored
    sequence_type : str, either 'nucleic_acid', 'peptide', or 'glycan'
    model_folder : str representing folder where models are to be stored
    output_folder : str representing folder where output is to be stored
    automl_search_techniques : str representing which AutoML search technique should be performed, one of 'all', 'deepswarm', 'autokeras', 'tpot'
    max_runtime_minutes : int representing max runtime for model search in minutes
    num_folds : int representing num folds
    verbosity : int representing 0=not verbose, 1=verbose
    do_backup : bool representing if a backup should be performed
    do_auto_bin : bool representing if target values should be automatically binned
    bin_threshold : float representing threshold for positive and negative classes
    input_col : str representing input column name where sequences can be located
    target_col : str representing target column name where target values can be located
    pad_seqs : str indicating pad_seqs method, either 'max', 'min', 'average'
    augment_data : str, either 'none', 'complement', 'reverse_complement', or 'both_complements'
    dataset_robustness : bool indicating if data ablation study should be performed
    num_final_epochs : int representing number of final epochs to train final deepswarm model
    yaml_params : dict of extra deepswarm parameters, with keys 'max_depth' (int), 'ant_count' (int), 'epochs' (int)
    num_generations : int representing number of generations of tpot search
    population_size : int representing population size of tpot search
    run_interpretation : bool indicating if interpretation module should be executed
    interpret_params : dict of extra interpretation parameters, with keys 'sample_number_class_activation_maps' (int), 'class_activation_grad_modifier' (str), 'class_activation_layer_index' (int);
        'sample_number_saliency_maps' (int), 'saliency_map_grad_modifier' (str), 'saliency_map_layer_index' (int), 'sample_number_mutagenesis' (int)
    run_design : bool indicating if design module should be executed
    design_params :dict of extra design parameters, with keys 'k' (int), 'substitution_type' (str), 'target_y' (float), 'class_of_interest' (int), 'constraint_file_path' (str);
        'de_novo_num_seqs_to_test' (int), 'storm_num_seqs_to_test' (int), 'num_of_optimization_rounds' (int)
    
    Returns
    -------
    None
    """ 

    data_path = data_folder + data_file 

    if automl_search_techniques == 'all' or automl_search_techniques == 'deepswarm': 

        print("#################################################################################################")
        print("##############################            RUNNING DEEPSWARM           ###########################")
        print("#################################################################################################")

        # DeepSwarm AutoML method based on: 
        #      Byla, E. and Pang, W., 2019. DeepSwarm: Optimising Convolutional 
        #      Neural Networks using Swarm Intelligence. arXiv preprint arXiv:1905.07350.
        #   Script adapted from:
        #      https://github.com/Pattio/DeepSwarm

        # define run folder path to store generated models and data
        run_folder = 'deepswarm/multiclass_classification/'

        # refresh model folder
        if not os.path.isdir(model_folder + run_folder):
            os.mkdir(model_folder + run_folder)

        # refresh outputs folder
        if not os.path.isdir(output_folder + run_folder):
            os.mkdir(output_folder + run_folder)

        dsc = DeepSwarmClassification(data_path, model_folder + run_folder, output_folder + run_folder, max_runtime=max_runtime_minutes, num_folds=num_folds, sequence_type=sequence_type, do_auto_bin=do_auto_bin, bin_threshold=bin_threshold, verbosity=verbosity, yaml_params=yaml_params, num_final_epochs=num_final_epochs, input_col=input_col, target_col=target_col, pad_seqs=pad_seqs, augment_data=augment_data, multiclass=True, dataset_robustness=dataset_robustness, run_interpretation = run_interpretation, interpret_params = interpret_params, run_design = run_design, design_params = design_params)
        dsc.run_system()

        # create backup folder
        if do_backup:
            backup_folder = './backup/runs/' +  datetime.now().strftime('%Y%m%d') + '/' + run_folder
            # create folder to store model (if not existent)
            if not os.path.isdir(backup_folder):
                os.makedirs(backup_folder)

            # copy all contents to dated backup
            copy_full_dir(model_folder + run_folder, backup_folder + model_folder[2:])
            copy_full_dir(output_folder + run_folder, backup_folder + output_folder[2:])
        
    if automl_search_techniques == 'all' or automl_search_techniques == 'autokeras': 

        print("#################################################################################################")
        print("##############################            RUNNING AUTOKERAS           ###########################")
        print("#################################################################################################")
        
        # AutoKeras AutoML method based on: 
        #      Jin, H., Song, Q. and Hu, X., 2019, July. Auto-keras: An efficient neural architecture search system. 
        #      In Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & 
        #      Data Mining (pp. 1946-1956). ACM.
        #   Script adapted from:
        #      https://github.com/keras-team/autokeras

        # define run folder path to store generated models and data
        run_folder = 'autokeras/multiclass_classification/'

        # refresh model folder
        if not os.path.isdir(model_folder + run_folder):
            os.mkdir(model_folder + run_folder)

        # refresh outputs folder
        if not os.path.isdir(output_folder + run_folder):
            os.mkdir(output_folder + run_folder)

        akc = AutoKerasClassification(data_path, model_folder + run_folder, output_folder + run_folder, max_runtime=max_runtime_minutes, num_folds=num_folds, sequence_type=sequence_type, do_auto_bin=do_auto_bin, bin_threshold=bin_threshold, verbosity=verbosity, input_col=input_col, target_col=target_col, pad_seqs=pad_seqs, augment_data=augment_data, multiclass=True, dataset_robustness=dataset_robustness, run_interpretation = run_interpretation, interpret_params = interpret_params, run_design = run_design, design_params = design_params)
        akc.run_system()

        # create backup folder
        if do_backup:
            backup_folder = './backup/runs/' +  datetime.now().strftime('%Y%m%d') + '/' + run_folder
            # create folder to store model (if not existent)
            if not os.path.isdir(backup_folder):
                os.makedirs(backup_folder)

            # copy all contents to dated backup
            copy_full_dir(model_folder + run_folder, backup_folder + model_folder[2:])
            copy_full_dir(output_folder + run_folder, backup_folder + output_folder[2:])
        
    if automl_search_techniques == 'all' or automl_search_techniques == 'tpot': 

        print("#################################################################################################")
        print("##############################            RUNNING TPOT                ###########################")
        print("#################################################################################################")

        # TPOT AutoML method based on: 
        #      Olson, R.S., Bartley, N., Urbanowicz, R.J. and Moore, J.H., 2016, July. Evaluation of a tree-based 
        #      pipeline optimization tool for automating data science. In Proceedings of the Genetic and Evolutionary 
        #      Computation Conference 2016 (pp. 485-492). ACM.
        #   Script adapted from:
        #      https://github.com/EpistasisLab/tpot

        # define run folder path to store generated models and data
        run_folder = 'tpot/multiclass_classification/'

        # refresh model folder
        if not os.path.isdir(model_folder + run_folder):
            os.mkdir(model_folder + run_folder)

        # refresh outputs folder
        if not os.path.isdir(output_folder + run_folder):
            os.mkdir(output_folder + run_folder)

        tpc = TPOTClassification(data_path, model_folder + run_folder, output_folder + run_folder, max_runtime=max_runtime_minutes, num_folds=num_folds, sequence_type=sequence_type, do_auto_bin=do_auto_bin, bin_threshold=bin_threshold, verbosity=verbosity, population_size=population_size, num_generations=num_generations, input_col=input_col, target_col=target_col, pad_seqs=pad_seqs, augment_data=augment_data, multiclass=True, dataset_robustness=dataset_robustness, run_interpretation = run_interpretation, interpret_params = interpret_params, run_design = run_design, design_params = design_params)
        tpc.run_system()

        # create backup folder
        if do_backup:
            backup_folder = './backup/runs/' +  datetime.now().strftime('%Y%m%d') + '/' + run_folder
            # create folder to store model (if not existent)
            if not os.path.isdir(backup_folder):
                os.makedirs(backup_folder)

            # copy all contents to dated backup
            copy_full_dir(model_folder + run_folder, backup_folder + model_folder[2:])
            copy_full_dir(output_folder + run_folder, backup_folder + output_folder[2:])

def run_regression(data_folder, data_file, sequence_type, model_folder, output_folder, automl_search_techniques, max_runtime_minutes, num_folds, verbosity, do_backup, do_transform, input_col, target_col, pad_seqs, augment_data, dataset_robustness, num_final_epochs, yaml_params, num_generations, population_size, run_interpretation, interpret_params, run_design, design_params):
    """run all three AutoML modules for regression
    Parameters
    ----------
    data_folder : str representing folder where data is stored
    data_file : str representing file name where data is stored
    sequence_type : str, either 'nucleic_acid', 'peptide', or 'glycan'
    model_folder : str representing folder where models are to be stored
    output_folder : str representing folder where output is to be stored
    automl_search_techniques : str representing which AutoML search technique should be performed, one of 'all', 'deepswarm', 'autokeras', 'tpot'
    max_runtime_minutes : int representing max runtime for model search in minutes
    num_folds : int representing num folds
    verbosity : int representing 0=not verbose, 1=verbose
    do_backup : bool representing if a backup should be performed
    do_transform : bool representing if target values should be transformed
    input_col : str representing input column name where sequences can be located
    target_col : str representing target column name where target values can be located
    pad_seqs : str indicating pad_seqs method, either 'max', 'min', 'average'
    augment_data : str, either 'none', 'complement', 'reverse_complement', or 'both_complements'
    dataset_robustness : bool indicating if data ablation study should be performed
    num_final_epochs : int representing number of final epochs to train final deepswarm model
    yaml_params : dict of extra deepswarm parameters, with keys 'max_depth' (int), 'ant_count' (int), 'epochs' (int)
    num_generations : int representing number of generations of tpot search
    population_size : int representing population size of tpot search
    run_interpretation : bool indicating if interpretation module should be executed
    interpret_params : dict of extra interpretation parameters, with keys 'sample_number_class_activation_maps' (int), 'class_activation_grad_modifier' (str), 'class_activation_layer_index' (int);
        'sample_number_saliency_maps' (int), 'saliency_map_grad_modifier' (str), 'saliency_map_layer_index' (int), 'sample_number_mutagenesis' (int)
    run_design : bool indicating if design module should be executed
    design_params :dict of extra design parameters, with keys 'k' (int), 'substitution_type' (str), 'target_y' (float), 'class_of_interest' (int), 'constraint_file_path' (str);
        'de_novo_num_seqs_to_test' (int), 'storm_num_seqs_to_test' (int), 'num_of_optimization_rounds' (int)
    
    Returns
    -------
    None
    """ 

    data_path = data_folder + data_file 

    if automl_search_techniques == 'all' or automl_search_techniques == 'deepswarm': 
        
        print("#################################################################################################")
        print("##############################            RUNNING DEEPSWARM           ###########################")
        print("#################################################################################################")

        # DeepSwarm AutoML method based on: 
        #      Byla, E. and Pang, W., 2019. DeepSwarm: Optimising Convolutional 
        #      Neural Networks using Swarm Intelligence. arXiv preprint arXiv:1905.07350.
        #   Script adapted from:
        #      https://github.com/Pattio/DeepSwarm

        # define run folder path to store generated models and data
        run_folder = 'deepswarm/regression/'

        # refresh model folder
        if not os.path.isdir(model_folder + run_folder):
            os.mkdir(model_folder + run_folder)

        # refresh outputs folder
        if not os.path.isdir(output_folder + run_folder):
            os.mkdir(output_folder + run_folder)

        dsc = DeepSwarmRegression(data_path, model_folder + run_folder, output_folder + run_folder, max_runtime=max_runtime_minutes, num_folds=num_folds, sequence_type=sequence_type, do_transform=do_transform, verbosity=verbosity, yaml_params=yaml_params, num_final_epochs=num_final_epochs, input_col=input_col, target_col=target_col, pad_seqs=pad_seqs, augment_data=augment_data, dataset_robustness=dataset_robustness, run_interpretation = run_interpretation, interpret_params = interpret_params, run_design = run_design, design_params = design_params)
        dsc.run_system()

        # create backup folder
        if do_backup:
            backup_folder = './backup/runs/' +  datetime.now().strftime('%Y%m%d') + '/' + run_folder
            # create folder to store model (if not existent)
            if not os.path.isdir(backup_folder):
                os.makedirs(backup_folder)

            # copy all contents to dated backup
            copy_full_dir(model_folder + run_folder, backup_folder + model_folder[2:])
            copy_full_dir(output_folder + run_folder, backup_folder + output_folder[2:])

    if automl_search_techniques == 'all' or automl_search_techniques == 'autokeras': 

        print("#################################################################################################")
        print("##############################            RUNNING AUTOKERAS           ###########################")
        print("#################################################################################################")
        
        # AutoKeras AutoML method based on: 
        #      Jin, H., Song, Q. and Hu, X., 2019, July. Auto-keras: An efficient neural architecture search system. 
        #      In Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & 
        #      Data Mining (pp. 1946-1956). ACM.
        #   Script adapted from:
        #      https://github.com/keras-team/autokeras

        # define run folder path to store generated models and data
        run_folder = 'autokeras/regression/'

        # refresh model folder
        if not os.path.isdir(model_folder + run_folder):
            os.mkdir(model_folder + run_folder)

        # refresh outputs folder
        if not os.path.isdir(output_folder + run_folder):
            os.mkdir(output_folder + run_folder)

        akc = AutoKerasRegression(data_path, model_folder + run_folder, output_folder + run_folder, max_runtime=max_runtime_minutes, num_folds=num_folds, sequence_type=sequence_type, verbosity=verbosity, do_transform=do_transform, input_col=input_col, target_col=target_col, pad_seqs=pad_seqs, augment_data=augment_data, dataset_robustness=dataset_robustness, run_interpretation = run_interpretation, interpret_params = interpret_params, run_design = run_design, design_params = design_params)       
        akc.run_system()

        # create backup folder
        if do_backup:
            backup_folder = './backup/runs/' +  datetime.now().strftime('%Y%m%d') + '/' + run_folder
            # create folder to store model (if not existent)
            if not os.path.isdir(backup_folder):
                os.makedirs(backup_folder)

            # copy all contents to dated backup
            copy_full_dir(model_folder + run_folder, backup_folder + model_folder[2:])
            copy_full_dir(output_folder + run_folder, backup_folder + output_folder[2:])

    if automl_search_techniques == 'all' or automl_search_techniques == 'tpot': 

        print("#################################################################################################")
        print("##############################            RUNNING TPOT                ###########################")
        print("#################################################################################################")

        # TPOT AutoML method based on: 
        #      Olson, R.S., Bartley, N., Urbanowicz, R.J. and Moore, J.H., 2016, July. Evaluation of a tree-based 
        #      pipeline optimization tool for automating data science. In Proceedings of the Genetic and Evolutionary 
        #      Computation Conference 2016 (pp. 485-492). ACM.
        #   Script adapted from:
        #      https://github.com/EpistasisLab/tpot

        # define run folder path to store generated models and data
        run_folder = 'tpot/regression/'

        # refresh model folder
        if not os.path.isdir(model_folder + run_folder):
            os.mkdir(model_folder + run_folder)

        # refresh outputs folder
        if not os.path.isdir(output_folder + run_folder):
            os.mkdir(output_folder + run_folder)

        tpc = TPOTRegression(data_path, model_folder + run_folder, output_folder + run_folder, max_runtime=max_runtime_minutes, num_folds=num_folds, sequence_type=sequence_type, verbosity=verbosity, do_transform=do_transform, population_size=population_size, num_generations=num_generations, input_col=input_col, target_col=target_col, pad_seqs=pad_seqs, augment_data=augment_data, dataset_robustness=dataset_robustness, run_interpretation = run_interpretation, interpret_params = interpret_params, run_design = run_design, design_params = design_params)
        tpc.run_system()

        # create backup folder
        if do_backup:
            backup_folder = './backup/runs/' +  datetime.now().strftime('%Y%m%d') + '/' + run_folder
            # create folder to store model (if not existent)
            if not os.path.isdir(backup_folder):
                os.makedirs(backup_folder)

            # copy all contents to dated backup
            copy_full_dir(model_folder + run_folder, backup_folder + model_folder[2:])
            copy_full_dir(output_folder + run_folder, backup_folder + output_folder[2:])

############## PART 4: WRAPPER FUNCTION FOR EVERYTHING ##############

def run_bioautomated(task, data_folder, data_file, sequence_type, model_folder, output_folder, automl_search_techniques = 'all', do_backup = False, max_runtime_minutes = 60, num_folds = 3, verbosity = 0,  do_auto_bin = True, bin_threshold = None, do_transform = True, input_col = 'seq', target_col = 'target', pad_seqs = 'max', augment_data = 'none', dataset_robustness = False, num_final_epochs = 50, yaml_params = {}, num_generations = 50, population_size = 50, run_interpretation = False, interpret_params = {}, run_design = False, design_params = {}):
    """run all three AutoML modules for binary classification
    Parameters
    ----------
    task : str, one of 'binary_classification', 'multiclass_classification', 'regression'
    data_folder : str representing folder where data is stored
    data_file : str representing file name where data is stored
    sequence_type : str, either 'nucleic_acid', 'peptide', or 'glycan'
    model_folder : str representing folder where models are to be stored
    output_folder : str representing folder where output is to be stored
    automl_search_techniques : str representing which AutoML search technique should be performed, one of 'all', 'deepswarm', 'autokeras', 'tpot'
    do_backup : bool representing if a backup should be performed
    max_runtime_minutes : int representing max runtime for model search in minutes
    num_folds : int representing num folds
    verbosity : int representing 0=not verbose, 1=verbose
    do_auto_bin : bool representing if target values should be automatically binned
    bin_threshold : float representing threshold for positive and negative classes
    do_transform : bool representing if target values should be transformed
    input_col : str representing input column name where sequences can be located
    target_col : str representing target column name where target values can be located
    pad_seqs : str indicating pad_seqs method, either 'max', 'min', 'average'
    augment_data : str, either 'none', 'complement', 'reverse_complement', or 'both_complements'
    dataset_robustness : bool indicating if data ablation study should be performed
    num_final_epochs : int representing number of final epochs to train final deepswarm model
    yaml_params : dict of extra deepswarm parameters, with keys 'max_depth' (int), 'ant_count' (int), 'epochs' (int)
    num_generations : int representing number of generations of tpot search
    population_size : int representing population size of tpot search
    run_interpretation : bool indicating if interpretation module should be executed
    interpret_params : dict of extra interpretation parameters, with keys 'sample_number_class_activation_maps' (int), 'class_activation_grad_modifier' (str), 'class_activation_layer_index' (int);
        'sample_number_saliency_maps' (int), 'saliency_map_grad_modifier' (str), 'saliency_map_layer_index' (int), 'sample_number_mutagenesis' (int)
    run_design : bool indicating if design module should be executed
    design_params :dict of extra design parameters, with keys 'k' (int), 'substitution_type' (str), 'target_y' (float), 'class_of_interest' (int), 'constraint_file_path' (str);
        'de_novo_num_seqs_to_test' (int), 'storm_num_seqs_to_test' (int), 'num_of_optimization_rounds' (int)
    
    Returns
    -------
    None
    """ 
     
    # refresh model folder
    if not os.path.isdir(model_folder):
        os.mkdir(model_folder)

    # refresh model folder
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)

    # refresh model and output folder
    if automl_search_techniques == 'all' or automl_search_techniques == 'deepswarm':  
        if not os.path.isdir(model_folder + 'deepswarm/'):
            os.mkdir(model_folder + 'deepswarm/')

        if not os.path.isdir(output_folder + 'deepswarm/'):
            os.mkdir(output_folder + 'deepswarm/')

    # refresh model and output folder
    if automl_search_techniques == 'all' or automl_search_techniques == 'autokeras': 
        if not os.path.isdir(model_folder + 'autokeras/'):
            os.mkdir(model_folder + 'autokeras/')

        if not os.path.isdir(output_folder + 'autokeras/'):
            os.mkdir(output_folder + 'autokeras/')

    # refresh model and output folder
    if automl_search_techniques == 'all' or automl_search_techniques == 'tpot': 
        if not os.path.isdir(model_folder + 'tpot/'):
            os.mkdir(model_folder + 'tpot/')

        if not os.path.isdir(output_folder + 'tpot/'):
            os.mkdir(output_folder + 'tpot/')

    # regardless of verbosity - these warnings are not meaningful
    tf.logging.set_verbosity(tf.logging.ERROR) # only errors
    
    if verbosity == 0:
        print("Verbosity set to 0. For more display items, set verbosity to 1.")
    else:
        print("Verbosity set to 1. For fewer display items, set verbosity to 0.")

    if task == 'binary_classification':
        print("#################################################################################################")
        print("#######################               RUNNING BINARY CLASSIFICATION            ##################")
        print("#################################################################################################")
        print('')
        run_binaryclass(data_folder, data_file, sequence_type, model_folder, output_folder, automl_search_techniques, max_runtime_minutes, num_folds, verbosity, do_backup, do_auto_bin, bin_threshold, input_col, target_col, pad_seqs, augment_data, dataset_robustness, num_final_epochs, yaml_params, num_generations, population_size, run_interpretation, interpret_params, run_design, design_params)

    elif task == 'multiclass_classification':
        print("#################################################################################################")
        print("#######################            RUNNING MULTICLASS CLASSIFICATION           ##################")
        print("#################################################################################################")
        print('')
        run_multiclass(data_folder, data_file, sequence_type, model_folder, output_folder, automl_search_techniques, max_runtime_minutes, num_folds, verbosity, do_backup, do_auto_bin, bin_threshold, input_col, target_col, pad_seqs, augment_data, dataset_robustness, num_final_epochs, yaml_params, num_generations, population_size, run_interpretation, interpret_params, run_design, design_params)
        
    elif task == 'regression':
        print("#################################################################################################")
        print("#######################               RUNNING REGRESSION                  #######################")
        print("#################################################################################################")
        print('')
        run_regression(data_folder, data_file, sequence_type, model_folder, output_folder, automl_search_techniques, max_runtime_minutes, num_folds, verbosity, do_backup, do_transform, input_col, target_col, pad_seqs, augment_data, dataset_robustness, num_final_epochs, yaml_params, num_generations, population_size, run_interpretation, interpret_params, run_design, design_params)

    else:
        print('Task is not valid. Please choose one of binary_classification, multiclass_classification, or regression.')

    print("BioAutoMATED has concluded.")
############## END OF FILE ##############