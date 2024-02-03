deep_gram_fillers = {'uh', 'um', 'mhmm', 'mm-mm', 'uh-uh', 'uh-huh', 'nuh-uh'}

# Write a function and main so that you get a string of each word as it is in the transcript from transcript.txt and return the number of filler words in the string
def filler_word_calculator():
    # also give me a percentage of the total words in the transcript that are fillers
    with open('transcript.txt', 'r') as file:
        transcript = file.read()
    words = transcript.split()
    filler_count = 0
    for word in words: 
        if word in deep_gram_fillers: 
            filler_count += 1 
    return filler_count, (filler_count / len(words)) * 100

def main():
    count, percentage = filler_word_calculator()
    print(f'The number of filler words in the transcript is {count} and the percentage of the total words in the transcript that are fillers is {percentage}%')


