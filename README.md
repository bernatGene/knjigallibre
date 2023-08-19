# knjigallibre

*Note; this is still very much WIP*

### Main idea

The idea is to design my own language learning app based on reading books, typing tests and a flashcard system for vocabulary.
At least for the time being, all the GUI will be terminal based. 
### Required resources
- Original text of the book in the target language
- (Optional) Translation of the book into a known language
- (Optional) Audio file of the text, for example an audiobook or from youtube. It may be useful to have the time-stampted transcript, but I'm thinking is not actually necessary

### Workflow
- In the main window, show a paragraph from the original text. 
- A word or a sentence is highlighted. 
- As you listen to the narration of the book, you try to follow the text by skipping on the highlighted word/sentence. Upon reaching a previously unknown word, the audio will stop, you will need to type it and understand its meaning. The app will allow you to search a translation, get a dictionay definition or find examples of the word used in sentences. 
- Of course at any given point, you may stop the narration, navigate the text to investigate the words and edit your notes. 
- Alternatively, you can skip the whole narration and just read the text on your own, skipping word by word, by sentence or just up to the next unknown word, all the while editing your notes, finding the meanings etc.  
- If you have a human translation of the source text, you can then show/hide the translation of the passage/paragraph so that you can understand the full context. 
- You will be maintaining a personal dictionary of words and expressions, as well as annotations on the text. 

#### Controls
In general, there will be a "control" and an "insert" mode, sort of like how vim works. The app should be generably usable without needing to use the mouse at any point. 

In this mode, we don't type the words, we interact with the app with the keyboard. 
- *Audio interaction*:
	- **Space** to pause/play the audio # is it necessary? can be done for the insert mode
	- **,** to skip forward in the audio 5 sec.
	- **.** to skip backwards in the audio 5 sec.
- *Text interaction:*  As the sound is playing, you should follow the text. The word you're reading is highlighted.
	- **J** jump to the next word
	- **K** jump to the prev word
	- **i** enter insert mode. Audio is stopped and you need to type the word to continue. Optionally, you can set it so that weakly known words will auto-enter the insert mode. 
		- On insert mode; in a separate window, the definition of the highlighted word is shown, together with some stats as how many times you have encountered it; and you can add notes about it. 
		- If we have a translated text, we can show as well the full paragraph translated. 
	- **ESC** exit insert mode.

### Layout

- A header with some information
- Sidebar/index/tools
- A couple paragraphs of the book
- Information window