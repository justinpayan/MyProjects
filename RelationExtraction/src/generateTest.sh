javac *java

java GenerateCSV TEST_FILE_FULL.TXT appendToEnd > TestCSV.csv
python AddWord2VecToCSV.py TestCSV.csv W2VTestCSV.csv appendToEnd 96
th read_csv.lua W2VTestCSV.csv test.th7 appendToEnd 96
