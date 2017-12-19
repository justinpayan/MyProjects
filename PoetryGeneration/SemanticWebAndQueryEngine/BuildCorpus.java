import org.apache.commons.io.*;
import java.io.*;
import java.util.Arrays;
import java.util.Stack;
import java.io.FileFilter;

//simply reads in a bunch of text files and concatenates them into one long text file, with \n\n between each paragraph.
public class BuildCorpus {
	
	private Stack<File> allTextFiles = new Stack<File>();

	public static void main(String[] args) {
		
		File oanc = new File("OANC/data/written_2/non-fiction");

		BuildCorpus instance = new BuildCorpus();	
		instance.pickOutTextFiles(oanc);
		
		File finalFile = new File("Final.txt");
		
		FileWriter writer = null;
		try {
			writer = new FileWriter(finalFile); //set up to write to the file
			while (!instance.allTextFiles.isEmpty()) {
				System.out.println(instance.allTextFiles.size());
				String file = FileUtils.readFileToString(instance.allTextFiles.pop()); //get a string representation of the file
				
				writer.write(file + "\n\n");
			}
			writer.close();
		}
		catch (Exception e) {
			System.out.println("Probably error writing files");
		}
	}

	public void pickOutTextFiles(File initDirOrFile) {

		if (initDirOrFile.isDirectory()) {
			File[] filesInDir = initDirOrFile.listFiles();
			for (int i=0; i<filesInDir.length; i++) {
				pickOutTextFiles(filesInDir[i]);
			}
		}
		else if (initDirOrFile.getName().endsWith(".txt")) {
			allTextFiles.push(initDirOrFile);
			System.out.println(initDirOrFile.getName());
		}
	}
}
