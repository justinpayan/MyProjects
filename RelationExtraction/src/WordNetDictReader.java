import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import edu.mit.jwi.Dictionary;
import edu.mit.jwi.IDictionary;
import edu.mit.jwi.item.IIndexWord;
import edu.mit.jwi.item.ISynset;
import edu.mit.jwi.item.ISynsetID;
import edu.mit.jwi.item.IWord;
import edu.mit.jwi.item.IWordID;
import edu.mit.jwi.item.POS;
import edu.mit.jwi.item.Pointer;

public class WordNetDictReader {

	WordNetDictReader() throws IOException {
		Init();
	}
	
	protected  void finalize() {
		Close();
	}
	
	IDictionary dict = null;
	void Init() throws IOException {		
		String wnhome = System.getenv("WNHOME");
		String path = wnhome + "/" + "dict";
		URL url = null;
		try{ url = new URL("file", null, path); } 
		catch(MalformedURLException e){ e.printStackTrace(); }
		   
		// construct the dictionary object and open it
		dict = new Dictionary(url);
		dict.open();	
	}
	
	void Close(){
		dict.close();
	}
	
	public static void main(String[] args) throws IOException{					
		String line;
		List syno = null;
		List hyno = null;
		BufferedReader br = null;

//		String pathToListOfWords = "C:\\Users\\Sujeet\\workspace\\WordNetProcessing\\ForWordNet.txt";
		String pathToListOfWords = "/Users/justinpayan/Desktop/Spring2016/KBS/FeatureExtraction/src/ForWordNet.txt";

		br = new BufferedReader(new FileReader(pathToListOfWords));

		WordNetDictReader reader = new WordNetDictReader(); 
			while ((line = br.readLine()) != null) {			
				System.out.println("\n" + line + "\n");
				syno = reader.GetSynonymsList(line);
				hyno = reader.GetHypernymList(line);
				
				for (Object str : syno) {
					System.out.println(str);
				}
				System.out.println();
				for (Object str : hyno) {
					System.out.println(str);
				}
			}

		  System.out.println(syno.size());
	      System.out.println(hyno.size());
	}
		
	List GetSynonymsList(String baseword) throws IOException {				    
		Integer maxsyn = 0;
		Integer MAX = 30;
	
		List syno = new ArrayList();
		IIndexWord idxWord = dict.getIndexWord(baseword, POS.NOUN);
	    if(idxWord == null) {			    	 		  			    	  
	    	for (int i = 0; i < MAX; i++) {
		      syno.add(baseword);
		    }		    	  
		    return syno;
	    } else {
	      	      
	       IWordID wordID = idxWord.getWordIDs().get(0);
	       IWord word = dict.getWord(wordID);
	      
	       ISynset synset = word.getSynset();

	       for( IWord w : synset.getWords () ) {
	    	  syno.add(w.getLemma());
	       }
      
	       if (maxsyn < syno.size() ) {
	    	  maxsyn = syno.size();
	       }
	      
	       if (syno.size() < MAX) {
	    	  int loop = MAX - syno.size();
	    	  String temp = "";
	    	  if (syno.size() < 1)
	    		  temp = baseword;
	    	  else
	    		  temp = (String) syno.get(0);
	    		  		    	 
	    	  for (int i = 0; i < loop; i++) {
	    		  syno.add(temp);
	    	  }
	       }       	      
      }

      return syno;
	}

	List GetHypernymList(String baseword) throws IOException {
		Integer maxhyn = 0;
		Integer MAX = 30;
		List hyno = new ArrayList();
		BufferedReader br = null;
		String line;
	
		IIndexWord idxWord = dict.getIndexWord(baseword, POS.NOUN);
	      if(idxWord == null) {			    	 
	    	  for (int i = 0; i < 30; i++) {
	    		  hyno.add(baseword);
	    	  }		    	  
	    	  return hyno;
		  } else {	      
	      
		      IWordID wordID = idxWord.getWordIDs().get(0);
		      IWord word = dict.getWord(wordID);
		      
		      ISynset synset = word.getSynset();	           
		      
		      List <ISynsetID> hypernyms = synset.getRelatedSynsets(Pointer.HYPERNYM) ;		    	      
		      List<IWord> words;
		      for(ISynsetID sid : hypernyms) {
		    	  words = dict.getSynset(sid).getWords() ;
			      for( Iterator<IWord> i = words.iterator(); i.hasNext();) {
			    	  String temp1 = i.next().getLemma();
			    	  hyno.add(temp1);	   
			      }      
		      }
		      
		      if (maxhyn < hyno.size()) {
		    	  maxhyn = hyno.size();
		      }
		      	   	      
		      if (hyno.size() < MAX) {
		    	  int loop = MAX - hyno.size();
		    	  String temp = "";
		    	  if (hyno.size() < 1)
		    		  temp = baseword;		    		  
		    	  else
		    		  temp = (String) hyno.get(0);
		    	 
		    	  for (int i = 0; i < loop; i++) {
		    		  hyno.add(temp);
		    	  }
		      }		      
	      }	
	      
	      return hyno;
		}		   			
	}
