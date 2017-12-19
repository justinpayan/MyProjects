import java.io.File;
import java.util.Scanner;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;

public class NistToCsv {
	public static void main(String[] args) {

		File directory = new File("TrainingSet/trainingset");
		File[] tempListing = directory.listFiles();

		File[] dirListing = new File[tempListing.length-2];

		for (int i=0; i<tempListing.length-2; i++) {
			dirListing[i] = tempListing[i+2];
		}

		int outputNum = 0;

		for (File child : dirListing) {

			outputNum++; 

			File output = new File("output" + outputNum + ".csv");
			FileWriter writer = null;
			Scanner scan = null;

			try {
				writer = new FileWriter(output);

				scan = new Scanner(child);

				String classifier = scan.nextLine();
				//writer.write(classifier);
				//we won't put the classifier, we just want the data now
				//we will make a separate file to classify the training examples

				writer.write("xCoord,yCoord\n");

				scan.nextDouble();
				while(scan.hasNextDouble()) {
					Double next1 = scan.nextDouble();
					Double next2 = scan.nextDouble();

					writer.write(next1.toString() + "," + next2.toString() + "\n");
					scan.nextDouble();
					scan.nextDouble();
				}
				writer.close();
			}
			catch (FileNotFoundException e) {
				System.out.println("Problem");
			}
			catch (IOException e) {
				System.out.println("IOException");
			}
		}
	}
}