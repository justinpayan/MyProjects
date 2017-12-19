import java.util.ArrayList;
import java.util.Stack;
import java.util.Scanner;
import java.util.Locale;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.FileWriter;

//Have the delimiter be . for sentences, and \n\n for paragraphs. Have an array (document)
//of arrays (paragraphs) of arrays that hold words (sentences). First count the words, sentences,
//and paragraphs in the document. Initialize the arrays appropriately. Add in the data. Have a 
//co-occurrence matrix, where each ij entry is the number of times word i co-occurs with word j.
//First you'll have to extract a word list. Make an arraylist with initial capacity of 2000. If the next word
//is already in the list, don't add it. Then get the size and that's the square co-occurrence matrix's size.
//Then I want a minimum number of co-occurrences so that the words have edges between them. How
//do I represent edges? Make an array of arrayLists with initial capacity 20. Put each word from the word
//list as the first element of the arrayLists. Add elements have a certain co-occurrence number.

//Just have a (corpus of) document(s) of paragraphs of words. Generate a list of words from that. Generate co-occurrence matrix.

//I want this to generalize to multiple documents. So have the method that generates the semantic web
//read in a list of documents. Then have an array that represents the corpus, filled with document arrays.
//Actually let's just start with reading in a single document.

public class SemWebLearn {
	
	//Will simply load the file and run the single file semantic web learner.
	//Then allows you to query the semantic web.
	public ArrayList<ArrayList<String>> wordWeb(File theDoc) {

		//File theDoc = new File("OANC/data/spoken/telephone/switchboard/20/sw2005-ms98-a-trans.txt");
		ArrayList<String> semWeb = docToParagraphs(theDoc);
		ArrayList<ArrayList<String>> wordWeb = paragraphsToWords(semWeb);

		/*

			Now I want the program to learn a word list, and print the word list. Only separate words, mind you.
			Also only words that appear more than 10 times in the corpus

		*/
		
		ArrayList<String> wordList = new ArrayList<String>();

		for (int i=0; i<wordWeb.size(); i++) {
			for (int j=0; j<wordWeb.get(i).size(); j++) {
				//only add words we don't already know
				if (!wordList.contains(wordWeb.get(i).get(j)))
					wordList.add(wordWeb.get(i).get(j));
			}
			System.out.println("Paragraphs left to search for word list: " + (wordWeb.size() - i));
		}		

		//write the word list to a text file named whatever you want it named
		Scanner userInput = new Scanner(System.in);
		System.out.println("What you wanna call the word list file?");
		String name = userInput.nextLine();
		File listFile = new File(name);
		
		try {
			FileWriter writer = new FileWriter(listFile);
			for (int i=0; i<wordList.size(); i++) {
				writer.write(wordList.get(i) + "\n");
			}
			writer.close();
		}
		catch (IOException e) {
			System.out.println("Something went wrong writing the word list to " + name);
			e.printStackTrace();
		}
		
		return wordWeb;
	} //end of wordWeb

	//Takes in a document theDoc. Returns a semantic web of type ArrayList<ArrayList<ArrayList<String>>> where the first word in each list
	//is a potential word to be queried and the rest of the words are associated with the first word. The 3 levels of the hierarchy are needed for
	//paragraphs, sentences, and words. The entire list represents the document. Later I can add one level at the top that will allow multiple
	//documents, and the entire list will represent a corpus.
	

	public static ArrayList<String> docToParagraphs(File theDoc) {
		
		ArrayList<String> semWeb = null;

		try {
			//How many paragraphs are in the document?
			int numPara = 0;
			
			Scanner paragraphs = new Scanner(theDoc);
			paragraphs.useDelimiter("\n\n");

			while (paragraphs.hasNext()) {
				numPara++;
				paragraphs.next();
			}

			//Have a new scanner that actually does the task of reading the file.
			Scanner paragraphs1 = new Scanner(theDoc);
			paragraphs1.useDelimiter("\n\n");

			//Read the file paragraph by paragraph.
			semWeb = new ArrayList<String>(numPara);
			
			int count = 0;
			while (paragraphs1.hasNext()) {
				System.out.println(count + " paragraphs read");
				semWeb.add(paragraphs1.next());
				count++;
			}
		}
		catch (FileNotFoundException e) {
			System.out.println("File not found");
		}
		
		return semWeb;
	}  //end of paragraphs to sentences method
	
	//parses a paragraph into its component words
	public static ArrayList<ArrayList<String>> paragraphsToWords(ArrayList<String> paragraphs) {

		ArrayList<ArrayList<String>> words = new ArrayList<ArrayList<String>>(paragraphs.size());

		String nextWord = "";

		for (int i=0; i<paragraphs.size(); i++) {
			ArrayList<String> theParagraph = new ArrayList<String>();
			Scanner scan = new Scanner(paragraphs.get(i));
			scan.useDelimiter(" |\n");

			while (scan.hasNext()) {
				nextWord = scan.next();
				nextWord.trim(); //words should have no white-space
				if (!nextWord.isEmpty()) {
					//words also should not have .'s or ,'s or "s or )'s or ]'s or next lines or spaces at the end of them
					while (!nextWord.isEmpty() && (nextWord.charAt(nextWord.length()-1) == '.' || nextWord.charAt(nextWord.length()-1) == ',' || nextWord.charAt(nextWord.length()-1) == '”' || nextWord.charAt(nextWord.length()-1) == '\n') || !((nextWord.charAt(nextWord.length()-1) > 64 && nextWord.charAt(nextWord.length()-1) < 91) || (nextWord.charAt(nextWord.length()-1) > 96 && nextWord.charAt(nextWord.length()-1) < 123))) {
						nextWord = nextWord.substring(0, nextWord.length()-1);
						if (nextWord.length() == 0)
							break; //this had to be done, because otherwise when it got down to zero it would mess up
					}
				}

				//words should not have "s or next lines or ('s or ['sat the start of them
				if (!nextWord.isEmpty()) {
					while (!nextWord.isEmpty() && !((nextWord.charAt(0) > 64 && nextWord.charAt(0) < 91) || (nextWord.charAt(0) > 96 && nextWord.charAt(0) < 123))) {						nextWord = nextWord.substring(1, nextWord.length());
					}
				}
			
				//words also should be in all lowercase
				nextWord = nextWord.toLowerCase();

				//if the word didn't consist of any letters or numbers it will be empty now, or a really weird character
				if (!nextWord.isEmpty()) {
					theParagraph.add(nextWord);
		
				}
			}
			words.add(theParagraph);
			System.out.println("Segmenting paragraph " + i + " of " + paragraphs.size());
		}

		return words;
	}
} //end of class
