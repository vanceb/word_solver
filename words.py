import os
import re
import argparse

LETTERS = 'abcdefghijklmnopqrstuvwxyz'


class words:
    '''
    Base class for word indexers

    This class forms the base class for word indexers.  Depending on the
    "normalisation" function which is used to create the key for the index
    a number of different indexes can be created, such as anagram index, or
    a crossword index.  These examples have been implemented later in this
    source code file and can be used as references.
    '''

    def __init__(self, word_index=None):
        '''
        Initialise the word index

        Args:
            word_index (dict): A word index to initialise with.  If None then
                               you can add words individually using the
                               add_word() method or from a file using the
                               load_words() method.
        '''
        if word_index is None:
            self.word_index = {}
        else:
            self.word_index = word_index

    def __repr__(self):
        return '{}({})'.format(self.__class__,
                               self.word_index
                               )

    def __str__(self):
        '''
        Provide a representation of the class
        '''
        return ('A word index of type ({})' +
                'containing {} entries'.format(self.__class__,
                                               len(self.word_list)
                                               )
                )

    def help_text(self):
        '''
        Print help for the word matcher

        Should be overidden by each subclss to provide detail on how to search
        using the indexer
        '''
        print('''
    This is a basic indexer that matches words in a case insensitive manner.
    Type a word in any or mixed case and if the word exists in the dictionary
    it will show you the word.

    Example:

        : HeLlo
        HELLO
              ''')

    def add_word(self, word):
        '''
        Add a word to the index

        Args:
            word (str):  The word to be indexed

        Returns:
            self
        '''
        # Normalise the word according to the class rules
        norm = self.normalise(word)
        # Add the word to the index with a key of the normalised word
        if norm in self.word_index:
            # Depending on the normalisation we may have multiple words woth
            # the same index key, so we need to store a list of words...
            self.word_index[norm].append(word)
        else:
            self.word_index[norm] = [word]
        return self

    def normalise(self, word):
        '''
        Normalise the word before indexing

        This function should return a tuple of the word itself and its index
        under the indexing scheme.  This function should be overridden by child
        classes as it is this which determines the key for the word index.

        Args:
            word (str): The word to be normalised

        Returns:
            (str): A normalised version of the word to be used as the index key
        '''

        # A simple normalisation
        return word.lower().strip()

    def load_words(self, filename, reset=True):
        '''
        Load reference word list from a file

        File should contain a single word per line

        Args:
            filename (str): location of the wordlist to use
            reset (bool): Whether to clear the current list

        Returns:
            itself
        '''

        if reset:
            # Start with an empty word list
            self.word_index = {}
        # Get the full path to the word file
        path = os.path.abspath(filename)
        # we will count how many words we index
        count = 0
        lines = 1
        # Check that the word file exists
        if os.path.exists(path):
            with open(path, 'r') as f:
                for line in f:
                    # Get the word from the file
                    w = line.strip()
                    # Check we only have one word on the line
                    words = w.split()
                    if len(words) > 1:
                        print("Multiple words (" +
                              w + ") found in line " + str(lines))
                    # Check for blank lines
                    elif w == '':
                        print("Blank line in word file:  " + str(lines))
                    # Check for non letter characters
                    elif any(char not in LETTERS for char in w.lower()):
                        print("Found non letter character in " +
                              w + " on line " + str(lines))
                    else:
                        # Add the word to the index
                        self.add_word(w)
                        count += 1
                    lines += 1
            print("Loaded " + str(count) + " words")
        return self

    def search(self, word):
        '''
        Search for a word in the index

        Looks for the word in the index using the normalisation lookup.
        Depending on the normalisation and therefore index key this may return
        more than one value.  This function therefore returns a list, which may
        contain a single item.  The function returns None if no match.
        '''

        # Normalise the word so we can match it in the index
        norm = self.normalise(word)
        # Is it in the index?
        if norm in self.word_index:
            # Return a list of words that match the index
            # There may be more than one and we always return a list
            # even if there is only one hit (Unless no hits)
            return self.word_index[norm]
        else:
            # If no hits then we return None
            return None


class anagram(words):

    def help_text(self):
        '''
        Print help for the word matcher

        Should be overidden by each subclss to provide detail on how to search
        using the indexer
        '''
        print('''
    Finds words that are an anagram of the input text

    Example:

        : opst
        OPTS
        POST
        POTS
        SPOT
        STOP
        TOPS
              ''')

    def normalise(self, word):
        '''
        Normalise the word for anagram matching

        To match anagrams we create a tuple of all of the letters in the word
        sorted alphabetically, then any word containing the same letters will
        normalise to the same value which is our index lookup...
        '''

        word = super().normalise(word)
        letters = []
        for letter in word:
            letters.append(letter)
        return tuple(sorted(letters))


class crossword(words):

    def help_text(self):
        '''
        Print help for the word matcher

        Should be overidden by each subclss to provide detail on how to search
        using the indexer
        '''
        print('''
    Finds words that match the input with blanks.  Blanks are considered to be
    any character that isn't a letter, so any punctuation or digits can be
    used for the blanks.

    Example:
        : __g_nt
        COGENT
        NUGENT
        REGENT
        URGENT
              ''')

    def search(self, word):
        '''
        Search through the index with missing letters

        Crossword search is long winded as we must look at each entry in the
        index to see whether we match it.  There is no easy lookup we can
        perform to narrow down the search space, so this search gets much
        slower with larger word lists
        '''

        # Build a regex incrementally from the incoming search term
        pattern = ''
        for letter in word.lower():
            if letter in LETTERS:
                # match the letter itself
                pattern += letter
            else:
                # match any letter
                pattern += '.'
        # Compile the search pattern to speed up matching
        matcher = re.compile(pattern)
        # Create an empty list for our matches
        hits = []
        # Loop over all of the indexed words
        for word in self.word_index:
            # See if it could be a match
            result = matcher.fullmatch(word)
            if result:
                # If it is then ad it to our matches
                # Because of how we are indexing there should only be one word
                # match per index entry so use the first word word[0]
                hits.append(self.word_index[word][0])
        return hits


class codeword(words):

    def help_text(self):
        '''
        Print help for the word matcher

        Should be overidden by each subclss to provide detail on how to search
        using the indexer
        '''
        print('''
    Finds words that match the input with missing letters.  This is similar to
    the crossword mode, but it treats the blank characters differently.  Each
    blank character matches only a single letter throughout the word.  If you
    have different letters through the word you must use different blank
    characters for each one.  Any non letter character can be used as a blank,
    e.g. digits or punctuation.


    Example:
        : 1234566t
        BAREFOOT
        DISCREET

        Note the double 6 towards the end of the search means that those two
        letters must be the same in the result and they must also be different
        from any of the other letters at the beginning which use 1-5...

              ''')

    def normalise(self, word):
        '''
        Normalise word for codeword matching

        With codewords we have a bit more knowledge of the problem.  We know
        where letters are the same and where they are different because of
        their code number.  We can use this information to speed our lookup by
        indexing a code that relates to our word.  Each letter in the word is
        given its own number, repeated letters get the same number.  We can
        them match on word structure before looking through the possible
        matches for those that could be a real match.  But this structured
        search drastically cuts the number of words that have to be checked
        fully...
        '''

        # Strip and lowercase the incoming word
        word = super().normalise(word)
        # Start with a blank code
        code = []
        # Keep track of the letters we have already seen
        letters_seen = {}
        # The number we are going to use for the next unique letter
        next_letter = 1
        # Loop over the letters in the word to create the code
        for letter in word:
            if letter not in letters_seen:
                # Add it and keep track of its number
                letters_seen[letter] = next_letter
                # Increment the code for the next unique letter
                next_letter += 1
            # Add the letter code to our list of letter codes
            code.append(letters_seen[letter])
        # Return a tuple as we will use it as a key to the index
        # Lists cannot be used as keys
        return tuple(code)

    def search(self, word):
        # We have no matches so far...
        matches = None
        # Normalise the search word to get the code
        norm = self.normalise(word)
        # Check to see whether we have the code in the index
        if norm in self.word_index:
            # We do so get the possible matches
            possibles = self.word_index[norm]
            # We must have at lease one hit so we are going to return a list
            matches = []
            # Loop over all possible matches
            for w in possibles:
                # Assume match until we find out differently
                failed = False
                # Loop over each letter in the word
                for i in range(len(word)):
                    # Is it a letter?
                    if word[i] in LETTERS:
                        # Is it the same as the letter in the possible match?
                        if word[i].lower() != w[i].lower():
                            # It isn't so let's get out of here
                            failed = True
                            break
                # If it matched all letters that we know about
                if not failed:
                    # Add it to our matches
                    matches.append(w)
        return matches


def main():
    # Use command line arguments
    parser = argparse.ArgumentParser()
    # Dictionary file with default
    parser.add_argument("-d",
                        "--dictionary",
                        default='dictionary.txt',
                        help="Dictionary file"
                        )
    # Which kind of index and search do we want
    parser.add_argument("type",
                        help="Type of index you require",
                        )

    # Parse the command line
    args = parser.parse_args()

    # Valid index options
    valid = ["plain", "anagram", "crossword", "codeword"]

    if args.type in valid:
        # Choose our index type based on user request
        if args.type == "plain":
            indx = words()
        if args.type == "anagram":
            indx = anagram()
        if args.type == "crossword":
            indx = crossword()
        if args.type == "codeword":
            indx = codeword()

        # Load the words from the dictionary
        indx.load_words(args.dictionary)
        # Print the help for the type of search we want
        indx.help_text()
    else:
        # User didn't select a valid option so print the help
        parser.print_help()
        parser.exit()

    # Allow user to search interactively
    again = True
    # Loop until we want to exit
    while again:
        # Give the user a search prompt
        search_word = input(": ")
        # If they just hit return signal quit
        if search_word == "":
            again = False
        else:
            # Perform the search
            results = indx.search(search_word)
            if results is None or len(results) == 0:
                print("Nothing found!")
            else:
                # Print out the results
                for w in results:
                    print(w)


if __name__ == "__main__":
    main()
