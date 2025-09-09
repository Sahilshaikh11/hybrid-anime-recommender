from utils.common_funtions import read_yaml
from config.paths_config import *
from src.data_preprocessing import DataPreprocessor
from src.model_training import ModelTraining

if __name__ == "__main__":
    data_preprocessor = DataPreprocessor(ANIMELIST_CSV, PROCESSED_DIR)
    data_preprocessor.run()

    model_trainer = ModelTraining(data_path=PROCESSED_DIR)
    model_trainer.train_model()