import java.util.Scanner;
import java.io.File;
import java.util.ArrayList;
import java.io.IOException;

//MENTION THAT I COULD IMPROVE THE ALGORITHM BY ONLY LOOKING AT WORDS WITH A CERTAIN NUMBER OF
//OCCURRENCES… E.G. IT COULD AVOID WORDS THAT NO ONE EVER USES… It can also remove these words from the paragraphs.


public class QuerySemWeb {
	public static void main(String[] args) {
		
		System.out.println("Reading large files. May take a minute.");
		
		SemWebLearn learner = new SemWebLearn();

		ArrayList<ArrayList<String>> doc = learner.wordWeb(new File(args[0]));

		//Read in the word list file that was just written by learner.
		System.out.print("Please re-enter the word list file name: ");
		Scanner input = new Scanner(System.in);
		String wordFileName = input.nextLine();
		File wordFile = new File(wordFileName);
		

		//read in the word list as an array
		ArrayList<String> wordList = new ArrayList<String>();

		try {
			Scanner scanner = new Scanner(wordFile);
			while (scanner.hasNext()) {
				wordList.add(scanner.next());
			}
		}
		catch (Exception e) {
			System.out.println("Something went wrong reading the word list file");
		}

		//The array list at a certain index holds a list of paragraphs where the corresponding word 
		//in the word list shows up
		ArrayList<ArrayList<Integer>> parasWhereWordsAre = new ArrayList<ArrayList<Integer>>();

		for (int i=0; i<wordList.size(); i++) {
			System.out.println("Counting paragraphs containing words: " + (wordList.size() - i));
			ArrayList<Integer> wheresWord = new ArrayList<Integer>();
			String currentWord = wordList.get(i);

			//generate list of paragraphs (indices in the semantic web's array list) the word is in
			for (int j=0; j<doc.size(); j++) {
				for (int k=0; k<doc.get(j).size(); k++) {
					if (doc.get(j).get(k).equals(currentWord) && !wheresWord.contains((Integer)(j))) {
						wheresWord.add((Integer)j);
					}
				}
			}
			parasWhereWordsAre.add(wheresWord);
		}

		int cutOff = 150; //the cutoff LLR value at which words are considered related
		//Now just query the user for words
		boolean notDone = true;
		while (notDone) {
			String lookup = ""; 
			boolean unacceptable = true;
			while (unacceptable) {
				
			System.out.println("Enter the word you want to look up: ");

			/*	try {
					while (System.in.available() != 0) {
						System.in.read(); //advance past all the next line tokens
					}
				}
				catch (IOException e) {
					
				}*/

				lookup = input.nextLine();
			
				if (wordList.contains(lookup))
					unacceptable = false;
				else
					System.out.println("I don't know that word. Please input another word: ");
			}

			//find the words that are related, using LLR test
			//You'll need the list of lists of Integers, parasWhereWordsAre
			double[] logLikeRat = new double[wordList.size()];

			//compute the relevant stuff (from the queried word) for the LLR test
			int numPara = doc.size();
			int indexQuer = wordList.indexOf(lookup);
			ArrayList<Integer> wheresQuer = parasWhereWordsAre.get(indexQuer); //list of paragraphs with the queried words
			int numWithQuer = wheresQuer.size(); //number of paras with the queried word
			double probQuer = ((double)numWithQuer)/numPara;

			for (int i=0; i<wordList.size(); i++) {
				//things I will need for the calculation
				String other = wordList.get(i);

				//we need to COPY values rather than simply assign because we don't want to change the
				//original values in the parasWhereWordsAre list
				ArrayList<Integer> wheresOth = new ArrayList<Integer>();
		
				for (int j=0; j<parasWhereWordsAre.get(i).size(); j++) {
					wheresOth.add(parasWhereWordsAre.get(i).get(j));
				}

				int numWithOth = wheresOth.size(); //number of paras with the queried word
				double probOth = ((double)numWithOth)/numPara;
	
				//the null hypothesis is that the probability distributions are independent
				double p11n = probQuer*probOth;
				double p21n = probQuer*(1-probOth);
				double p12n = (1-probQuer)*probOth;
				double p22n = (1-probQuer)*(1-probOth);

				//now we consider the alternative hypothesis, that the words' prob's are dependent on each other
				ArrayList<Integer> intersect = new ArrayList<Integer>(); //need a copy so we can find the intersection of the two
				ArrayList<Integer> copy2Quer = new ArrayList<Integer>();
				for (int j=0; j<numWithQuer; j++) {
					intersect.add(wheresQuer.get(j));
					copy2Quer.add(wheresQuer.get(j));
				}

				intersect.retainAll(wheresOth);

				double p11 = ((double)intersect.size())/numPara;
						
				copy2Quer.removeAll(intersect);
				ArrayList<Integer> noOther = copy2Quer;
				double p21 = ((double)noOther.size())/numPara;
		
				wheresOth.removeAll(intersect);
				ArrayList<Integer> noQuer = wheresOth;
				double p12 = ((double)noQuer.size())/numPara;
		
				double p22 = ((double)numPara - intersect.size())/numPara;

				//NOW WE COMPUTE THE LLR
				double sum = 0;
				sum += intersect.size()*Math.log(p11n/p11);
				sum += noQuer.size()*Math.log(p12n/p12);
				sum += noOther.size()*Math.log(p21n/p21);
				sum += (numPara - intersect.size())*Math.log(p22n/p22);
				
				logLikeRat[i] = (-2)*sum;
				//System.out.println(logLikeRat[i]);
				if (logLikeRat[i] > cutOff) {
					System.out.println(other);
				}
			}			

			System.out.println("\nThat's all of them!\n");

			System.out.println("Are you about done playing around with this program?\nPlease enter y or n: \nRemember you can also enter decreaseCutoff or increaseCutoff");
			String reply = input.nextLine();
			if (reply.equals("y")) 
				notDone = false;
			if (reply.equals("decreaseCutoff"))
				cutOff -= 25;
			if (reply.equals("increaseCutoff"))
				cutOff += 25;
		}
	}
}
