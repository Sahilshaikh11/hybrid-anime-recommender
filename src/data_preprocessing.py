import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
import sys

logger = get_logger(__name__)


class DataPreprocessor:
    def __init__(self, input, output_dir):
        self.input_file = input
        self.output_dir = output_dir

        self.rating_df = None
        self.anime_df = None
        self.x_train_array = None
        self.x_test_array = None
        self.y_train = None
        self.y_test = None

        self.user2user_encoded = {}
        self.user2user_decoded = {}
        self.anime2anime_encoded = {}
        self.anime2anime_decoded = {}

        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Data Processing Initialized.")

    def load_data(self, usecols):
        try:
            self.rating_df = pd.read_csv(self.input_file, low_memory=True, usecols=usecols)
            logger.info(f"Data loaded successfully from {self.input_file}.")
        except Exception as e:
            raise CustomException(f"Error loading data: {e}", sys)
        
    def filter_users(self, min_ratings=400):
        try:
            n_ratings = self.rating_df['user_id'].value_counts()
            self.rating_df = self.rating_df[self.rating_df['user_id'].isin(n_ratings[n_ratings >= min_ratings].index)]
            logger.info(f"Filtered users with at least {min_ratings} ratings.")
        except Exception as e:
            raise CustomException(f"Error filtering users: {e}", sys)
    
    def scale_ratings(self):
        try:
            min_rating = min(self.rating_df['rating'])
            max_rating = max(self.rating_df['rating'])

            self.rating_df['rating'] = self.rating_df['rating'].apply(lambda x: (x - min_rating) / (max_rating - min_rating)).values.astype(np.float32)
            logger.info("Ratings scaled to range [0, 1].")
        except Exception as e:
            raise CustomException(f"Error scaling ratings: {e}", sys)
        
    def encode_data(self):
        try:
            ### For USERS
            user_ids = self.rating_df["user_id"].unique().tolist()
            self.user2user_encoded = {x: i for i, x in enumerate(user_ids)}
            self.user2user_decoded = {i: x for i, x in enumerate(user_ids)}
            self.rating_df['user'] = self.rating_df['user_id'].map(self.user2user_encoded)

            ### For ANIME
            anime_ids = self.rating_df["anime_id"].unique().tolist()
            self.anime2anime_encoded = {x: i for i, x in enumerate(anime_ids)}
            self.anime2anime_decoded = {i: x for i, x in enumerate(anime_ids)}
            self.rating_df['anime'] = self.rating_df['anime_id'].map(self.anime2anime_encoded)

            logger.info("User and Anime IDs encoded.")
        except Exception as e:
            raise CustomException(f"Error encoding data: {e}", sys)
        
    def split_data(self, test_size=1000, random_state=43):
        try:
            self.rating_df = self.rating_df.sample(frac=1, random_state=random_state).reset_index(drop=True)
            X = self.rating_df[['user', 'anime']].values
            Y = self.rating_df['rating'].values

            train_indices = self.rating_df.shape[0] - test_size

            X_train, X_test, y_train, y_test = (
                X[:train_indices],
                X[train_indices:],
                Y[:train_indices],
                Y[train_indices:]
            )

            self.X_train_array = [X_train[:, 0], X_train[:, 1]]
            self.X_test_array = [X_test[:, 0], X_test[:, 1]]
            self.y_train = y_train
            self.y_test = y_test

            logger.info(f"Data split into training and testing sets with test size {test_size}.")
        except Exception as e:
            raise CustomException(f"Error splitting data: {e}", sys)
        
    def save_artifacts(self):
        try:
            artifacts = {
                'user2user_encoded': self.user2user_encoded,
                'user2user_decoded': self.user2user_decoded,
                'anime2anime_encoded': self.anime2anime_encoded,
                'anime2anime_decoded': self.anime2anime_decoded,
            }

            for name, data in artifacts.items():
                joblib.dump(data, os.path.join(self.output_dir, f"{name}.pkl"))
                logger.info(f"Saved artifact: {name}.pkl")

            joblib.dump(self.X_train_array, X_TRAIN_ARRAY)
            joblib.dump(self.X_test_array, X_TEST_ARRAY)
            joblib.dump(self.y_train, Y_TRAIN)
            joblib.dump(self.y_test, Y_TEST)

            self.rating_df.to_csv(RATING_DF, index=False)

            logger.info("All artifacts saved successfully.")
        except Exception as e:
            raise CustomException(f"Error saving artifacts: {e}", sys)
        
    def process_anime_data(self):
        try:
            df = pd.read_csv(ANIME_CSV)
            cols = ["MAL_ID", "Name", "Genres", "sypnopsis"]
            synopsis_df = pd.read_csv(ANIMESYNOPSIS_CSV, usecols=cols)

            df = df.replace("Unknown", np.nan)

            def getAnimeName(anime_id):
                try:
                    name = df[df['anime_id'] == anime_id].eng_version.values[0]
                    if name is np.nan:
                        name = df[df['anime_id'] == anime_id].Name.values[0]
                except:
                    print("Error")
                return name
            
            df["anime_id"] = df["MAL_ID"]
            df["eng_version"] = df["English name"]
            df["eng_version"] = df.anime_id.apply(lambda x: getAnimeName(x))

            df.sort_values(by="Score",
               ascending=False,
               inplace=True,
               kind="quicksort",
               na_position='last')
            
            df = df[["anime_id", "eng_version", "Score", "Genres", "Episodes", "Type", "Premiered", "Members"]]

            df.to_csv(DF, index=False)
            synopsis_df.to_csv(SYNOPSIS_DF, index=False)
            logger.info("Anime data processed and saved successfully.")
        except Exception as e:
            raise CustomException(f"Error processing anime data: {e}", sys)
        
    def run(self):
        try:
            self.load_data(usecols=['user_id', 'anime_id', 'rating'])
            self.filter_users()
            self.scale_ratings()
            self.encode_data()
            self.split_data()
            self.save_artifacts()

            self.process_anime_data()

            logger.info("Data preprocessing completed successfully.")
        except Exception as e:
            raise CustomException(f"Error in data preprocessing run: {e}", sys)
        
if __name__ == "__main__":
    data_preprocessor = DataPreprocessor(ANIMELIST_CSV, PROCESSED_DIR)
    data_preprocessor.run()