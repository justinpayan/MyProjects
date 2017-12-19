public class PoemWriter {
	public static void main(String[] args) {
		RandWord randomGenerator = new RandWord();
		
		for (int i = 0; i < 5; i++) {
			for (int j = 0; j<5; j++) {
				System.out.print(randomGenerator.newWord() + " ");
			}
			System.out.println();
		}
	}
}
