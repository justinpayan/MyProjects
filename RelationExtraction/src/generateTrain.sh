javac *java

java GenerateCSV TRAIN_FILE.TXT appendToEnd > TrainCSV.csv
python AddWord2VecToCSV.py TrainCSV.csv W2VTrainCSV.csv appendToEnd 96
th read_csv.lua W2VTrainCSV.csv train.th7 appendToEnd 96
