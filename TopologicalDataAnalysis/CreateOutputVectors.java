import java.io.File;
import java.util.Scanner;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;

/*
*
*
*	We have to sort the output vectors according to how R sorted 
*	the original data files. Thus 1 is first, then 10, then 100, etc.
*	
*	Some guesswork is taken out, because I have a sorted list that came
*	from R, detailing the exact order. 
*
*	Run this whole thing from the top TopoDataAnalysis directory
*
*/

public class CreateOutputVectors {

	public static void main(String[] args) {
		try {
		File file = new File("outputData/fileNames.csv");

		File outputFile = new File("outputVectors.csv");
		FileWriter writer = new FileWriter(outputFile);

		writer.write("PA,TA,TA_RS,RS,RS_TA,RS_WN,LS,LS_TA,WN,WN_RS,WN_RS_LS\n"); //so we have the classes listed at the top of the csv file

		File directory = new File("TrainingSet/trainingset");
		File[] tempListing = directory.listFiles();
		
		File[] printListing = new File[tempListing.length-2];

		for (int i=0; i<tempListing.length-2; i++) {
			printListing[i] = tempListing[i+2];
		}

		//we now have all of our original files (from Eric) in an array

		Scanner scan = new Scanner(file);

		scan.nextLine();
		scan.useDelimiter(",");

		while (scan.hasNext()) {
			scan.next();
			String next = scan.nextLine().substring(8);
			next = next.substring(0,next.length()-5);
			int toFind = Integer.decode(next);
			System.out.println(toFind);
			//printListing[toFind-1] is our fingerprint file corresponding to this
			Scanner printScanner = new Scanner(printListing[toFind-1]);
			String classification = printScanner.nextLine();

			switch (classification) {
				case "PA": 
					writer.write("1,0,0,0,0,0,0,0,0,0,0\n");
					break;
				case "TA": 
					writer.write("0,1,0,0,0,0,0,0,0,0,0\n");
					break;
				case "TA RS": 
					writer.write("0,0,1,0,0,0,0,0,0,0,0\n");
					break;
				case "RS": 
					writer.write("0,0,0,1,0,0,0,0,0,0,0\n");
					break;
				case "RS TA": 
					writer.write("0,0,0,0,1,0,0,0,0,0,0\n");
					break;
				case "RS WN": 
					writer.write("0,0,0,0,0,1,0,0,0,0,0\n");
					break;
				case "LS": 
					writer.write("0,0,0,0,0,0,1,0,0,0,0\n");
					break;
				case "LS TA": 
					writer.write("0,0,0,0,0,0,0,1,0,0,0\n");
					break;
				case "WN": 
					writer.write("0,0,0,0,0,0,0,0,1,0,0\n");
					break;
				case "WN RS": 
					writer.write("0,0,0,0,0,0,0,0,0,1,0\n");
					break;
				case "WN RS LS": 
					writer.write("0,0,0,0,0,0,0,0,0,0,1\n");
					break;
			}
		}
		writer.close();
		}
		catch (IOException e) {
			System.out.println("IOExcecption");
		}
		
		
	}

}