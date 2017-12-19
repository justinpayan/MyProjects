/**
 * Created by justinpayan on 4/27/16.
 * Will extract features for SemEval 2010 Task 8 Dataset
 * Right now those features only include dependency parse tree based features.
 */
import edu.stanford.nlp.international.Language;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.IndexedWord;
import edu.stanford.nlp.ling.TaggedWord;
import edu.stanford.nlp.parser.lexparser.IterativeCKYPCFGParser;
import edu.stanford.nlp.parser.nndep.DependencyParser;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import edu.stanford.nlp.trees.GrammaticalRelation;
import edu.stanford.nlp.trees.GrammaticalStructure;
import edu.stanford.nlp.trees.TypedDependency;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.StringReader;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import java.lang.Thread;
import java.lang.InterruptedException;


public class GenerateCSV {
    public static void main(String[] args) {
        try {

            // Set variables from command line
            boolean appendToEnd;
            if (args[1].equals("appendToEnd")) appendToEnd = true;
            else appendToEnd = false;

            // Initialize the POS tagger
            String taggerPath = "./edu/stanford/nlp/models/pos-tagger/english-left3words/english-left3words-distsim.tagger";
            MaxentTagger tagger = new MaxentTagger(taggerPath);

            // Initialize the dependency parser
            String modelPath = DependencyParser.DEFAULT_MODEL;
            DependencyParser parser = DependencyParser.loadFromModelFile(modelPath);

            // Load in the file
            File file = new File(args[0]);
            Scanner scan = new Scanner(file);
            String fileWords = "";

            while (scan.hasNextLine()) {
                fileWords += scan.nextLine() + "\n";
            }

            // Pull out all 8000 sentences
            String[] cleanSentences = new String[8000];
            Pattern pattern = Pattern.compile("\\d+\\t\\\".+\\\"\\n");
            Matcher matcher = pattern.matcher(fileWords);
            int index = 0;
            while(matcher.find()) {
                // Remove quotes
                cleanSentences[index] = matcher.group().replaceAll("\\\"","")
						.replaceAll("\\d+\\t","")						
						/*
                                            .replaceAll("\\<e[1||2]\\>","")
                                            .replaceAll("\\</e[1||2]\\>","") + "\n"*/;
//                System.err.println(cleanSentences[index]);
                index++;
            }

            // Pull out the classes of those sentences
            pattern = Pattern.compile("\\\"\\n(.+\\((e1|e2),(e1|e2)\\)|Other)\\n");
            matcher = pattern.matcher(fileWords);
            int classIndex = 0;
            String[] classes = new String[8000];

            while (matcher.find()) {
                classes[classIndex] = matcher.group().replaceAll("\\\"","").replaceAll("\\n","");
//                System.err.println(classes[classIndex]);
                classIndex++;

            }

            classIndex = 0;
            int[] intClasses = mapToInts(classes);

            // For every sentence, extract features.
            // Be careful of sentences that the tokenizer turns into two sentences.

            WordNetDictReader reader = new WordNetDictReader();
            int maxSentenceSize = 0;

            for (String text : cleanSentences) {
                if (text!=null) {
                    System.err.println(classIndex);
                    DocumentPreprocessor tokenizer = new DocumentPreprocessor(new StringReader(text));
                    Iterator<List<HasWord>> iterator = tokenizer.iterator();
                    List<HasWord> sentence = tokenizer.iterator().next();
                    while (iterator.hasNext()) {
                        sentence.addAll(iterator.next());
                        System.err.println("Happened");
                    }

                    // Get the 0-based index of e1 and e2, then remove the e1 and e2 tags
                    // Note that we are assuming single indices will be enough. Some of the entities
                    // actually have multiple words and might need to be dealt with accordingly.
                    int e1Index = -1;
                    int e2Index = -1;
                    for (int i = 0; i < sentence.size(); i++) {
                        if (sentence.get(i).word().equals("<e1>")) {
                            e1Index = i;
                            sentence.remove(i);
                            i -= 1;
                        } else if (sentence.get(i).word().equals("</e1>")) {
                            sentence.remove(i);
                            i = sentence.size() + 5;
                        }
                    }

                    for (int i = 0; i < sentence.size(); i++) {
                        if (sentence.get(i).word().equals("<e2>")) {
                            e2Index = i;
                            sentence.remove(i);
                            i -= 1;
                        } else if (sentence.get(i).word().equals("</e2>")) {
                            sentence.remove(i);
                            i = sentence.size() + 5;
                        }
                    }

                    if (e1Index == -1 || e2Index == -1) {
                        System.err.println("We've got a problem");
                        System.err.println(sentence);
                        System.err.println(iterator.hasNext());
                        System.err.println(text);
                    }

                    // Cut out sentences that do not have e1 or e2. These are
                    // precisely those sentences that the Stanford parser cut in half.
                    if (e1Index != -1 && e2Index != -1) {

//                    System.err.println(sentence);
//                        System.err.println(e1Index + " " + e2Index);
//                    System.err.println(classIndex);

                        if (sentence.size() > maxSentenceSize) {
                            maxSentenceSize = sentence.size();
                        }
                        // Get the dependency path between the two words in terms of just indices.
                        // Then for any HasWord in the sentence, can call a.index() and figure out
                        // if our list of indices in the path contains that index.

                        List<TaggedWord> tagged = tagger.tagSentence(sentence);
                        GrammaticalStructure gs = parser.predict(tagged);
                        //                for (TaggedWord currentWord : tagged) {
                        //                    System.out.print(currentWord.word() + " ");
                        //                }
                        //                System.out.println();
                        //                System.out.println(gs);
                        //                System.out.println();
                        List<TypedDependency> td = gs.typedDependencies(GrammaticalStructure.Extras.NONE);
                        List<IndexedWord> path = findPath(td, sentence.get(e1Index).word(), sentence.get(e2Index).word(), e1Index + 1, e2Index + 1); // indices are 1 based in typed dependencies
                        for (IndexedWord word : path) {
                            //                    System.out.println(word.word() + " " + word.index());
                        }


                        Map<String, Integer> uDeps = getUnivDepsMap();

                        // For each typedDependency in gs, flip the bit for that word and dependency
                        boolean[][] depTypes = new boolean[sentence.size()][uDeps.keySet().size()];
                        for (TypedDependency typedDependency : td) {
                            //                    System.out.println(typedDependency);
                            //                    System.out.println(typedDependency.gov());
                            //                    System.out.println(typedDependency.dep());
                            //                    System.out.println(typedDependency.reln());
                            //                    System.out.println(uDeps.get(typedDependency.reln().toString()));
                            if (typedDependency.gov().index() > 0)
                                depTypes[typedDependency.gov().index() - 1][uDeps.get(typedDependency.reln().toString())] = true;
                            if (typedDependency.dep().index() > 0)
                                depTypes[typedDependency.dep().index() - 1][uDeps.get(typedDependency.reln().toString())] = true;
                        }

                        // Iterate through each word in the sentence and write it out along with its features.

                        for (int i = 0; i < sentence.size() - 1; i++) {
                            // Write the word
                            System.out.print("str_feat_" + sentence.get(i) + "\t");

                            if (!appendToEnd) {
                                // Write out the first hypernym and first synonym
                                List synonyms = reader.GetSynonymsList(sentence.get(i).word());
                                List hypernyms = reader.GetHypernymList(sentence.get(i).word());
                                System.out.print("wn_str_feat_" + synonyms.get(0) + "\t");
                                System.out.print("wn_str_feat_" + hypernyms.get(0) + "\t");
                            }


                            // print out vectors representing the distance from e1 and e2
                            int distE1 = (int) Math.abs(i - e1Index);
                            System.out.print(distE1 + "\t" + distE1 + "\t" + distE1 + "\t" + distE1 + "\t" + distE1 + "\t");

                            int distE2 = (int) Math.abs(i - e2Index);
                            System.out.print(distE2 + "\t" + distE2 + "\t" + distE2 + "\t" + distE2 + "\t" + distE2 + "\t");

                            // Is on path?
                            int onPath = 0;
                            if (e1Index == i) onPath = 1;
                            else {
                                for (IndexedWord word : path) {
                                    if (word.index() - 1 == i) onPath = 1;
                                }
                            }

                            System.out.print(onPath + "\t");

                            for (int j = 0; j < depTypes[i].length; j++) {
                                if (depTypes[i][j]) System.out.print(1 + "\t");
                                else System.out.print(0 + "\t");
                            }
                        }

                        if (appendToEnd) {
                            // Print out the synonyms and hypernyms of e1 and e2
                            List synonymsE1 = reader.GetSynonymsList(sentence.get(e1Index).word());
                            List hypernymsE1 = reader.GetHypernymList(sentence.get(e1Index).word());
                            List synonymsE2 = reader.GetSynonymsList(sentence.get(e2Index).word());
                            List hypernymsE2 = reader.GetHypernymList(sentence.get(e2Index).word());
                            for (Object a : synonymsE1) System.out.print("wn_str_feat_" + a + "\t");
                            for (Object a : hypernymsE1) System.out.print("wn_str_feat_" + a + "\t");
                            for (Object a : synonymsE2) System.out.print("wn_str_feat_" + a + "\t");
                            for (Object a : hypernymsE2) System.out.print("wn_str_feat_" + a + "\t");
                        }

                        //Write out the class of the sentence.
                        System.out.print(intClasses[classIndex] + "\t");
                        classIndex++;

                        // Write out metadata, namely sentence length and distance between e1 and e2
                        System.out.print(sentence.size()-1 + "\t" + Math.abs(e1Index-e2Index) + "\n");
                    } else {
                        classIndex++;
                    }
                }
            }
            System.err.println("Max sentence size is: " + maxSentenceSize);
        }
        catch(IOException e) {System.err.println("IOException Occurred");}
    }

    // Recursive method to find path between two IndexedWords in the parse tree
    //
    public static List<IndexedWord> findPath(List<TypedDependency> td, String word1, String word2, int index1, int index2) {
        for (TypedDependency a : td) {
            IndexedWord stepWord = null;
//            System.out.println(a);
//            System.out.println(word1);
//            System.out.println(word2);

            if (word1.equals(a.gov().word()) && index1 == a.gov().index()) {
                stepWord = a.dep();
            } else if (word1.equals(a.dep().word()) && index1 == a.dep().index()) {
                stepWord = a.gov();
            }
//            System.out.println(stepWord + "\n");
            if (stepWord != null && stepWord.word() != null) {
                if (word2.equals(stepWord.word()) && index2 == stepWord.index()) {
                    ArrayList<IndexedWord> toReturn = new ArrayList<IndexedWord>();
                    toReturn.add(stepWord);
                    return toReturn;
                } else {
                    List<TypedDependency> newtd = new ArrayList<TypedDependency>(td);

                    newtd.remove(a);
                    List<IndexedWord> restOfPath = findPath(newtd, stepWord.word(), word2, stepWord.index(), index2);
                    if (restOfPath != null) {
                        restOfPath.add(stepWord);
                        return restOfPath;
                    }
                }
            }
        }
        return null;
    }

    /*
    *
    * Generate a map that maps all of the Universal Dependencies to integers.
    * There are 40 universal relations, and 7 more that are English-specific.
    * The specific to English relations are given at universaldependencies.org/ext-dep-index.html
    * The 40 others are at universaldependencies.org/u/dep/index.html
    *
    * */

    public static Map<String, Integer> getUnivDepsMap() {

        HashMap<String, Integer> uDeps = new HashMap<String, Integer>();
        String[] deps = { // Originals
                        "acl","advcl","advmod","amod","appos","aux","auxpass","case",
                        "cc","ccomp","compound","conj","cop","csubj","csubjpass",
                        "dep","det","discourse","dislocated","dobj","expl","foreign",
                        "goeswith","iobj","list","mark","mwe","name","neg","nmod",
                        "nsubj","nsubjpass","nummod","parataxis","punct","remnant",
                        "reparandum","root","vocative","xcomp",
                        // English-specific
                        "acl:relcl","cc:preconj","compound:prt","det:predet","nmod:npmod",
                        "nmod:poss","nmod:tmod"};
        for (int i=0; i<deps.length; i++) {
//            GrammaticalRelation toPut = GrammaticalRelation.valueOf(Language.English,deps[i]);
            uDeps.put(deps[i],(Integer)i);
        }
        return uDeps;
    }

    public static int[] mapToInts(String[] inArray) {

        HashMap<String, Integer> map = new HashMap<String,Integer>();
        for (Object a : inArray) System.err.println(a);
        System.err.println(inArray.length);
        int[] toReturn = new int[inArray.length];

        map.put("Component-Whole(e2,e1)", 1);
        map.put("Member-Collection(e2,e1)", 10);
        map.put("Entity-Origin(e1,e2)", 11);
        map.put("Entity-Destination(e2,e1)", 19);
        map.put("Product-Producer(e1,e2)", 15);
        map.put("Content-Container(e1,e2)", 7);
        map.put("Message-Topic(e2,e1)", 14);
        map.put("Instrument-Agency(e1,e2)", 18);
        map.put("Cause-Effect(e1,e2)", 12);
        map.put("Component-Whole(e1,e2)", 13);
        map.put("Content-Container(e2,e1)", 17);
        map.put("Message-Topic(e1,e2)", 8);
        map.put("Entity-Origin(e2,e1)", 16);
        map.put("Product-Producer(e2,e1)", 9);
        map.put("Entity-Destination(e1,e2)", 6);
        map.put("Instrument-Agency(e2,e1)", 3);
        map.put("Member-Collection(e1,e2)", 4);
        map.put("Other", 2);
        map.put("Cause-Effect(e2,e1)", 5);

        for (int i=0; i<inArray.length; i++) {
            if (inArray[i] != null) {
                System.err.println(i);
                System.err.println(inArray[i]);
                toReturn[i] = map.get(inArray[i]);
            }
        }

//        for (int i=0; i<inArray.length; i++) {
//            if (!map.containsKey(inArray[i])) map.put(inArray[i], map.keySet().size() + 1);
//            toReturn[i] = map.get(inArray[i]);
//        }
//
//	for (String a: map.keySet()) {
//		System.err.println(a + " " + map.get(a));
//	}
        return toReturn;
    }
}
