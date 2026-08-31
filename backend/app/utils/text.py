def extract_sentence(passage, start_position, end_position):
    sentence_start = start_position
    sentence_end = end_position
    while sentence_start > 0 and passage[sentence_start - 1] not in ".?!":
        sentence_start -= 1
    while sentence_end < len(passage)-1 and passage[sentence_end] not in ".?!":
        sentence_end += 1
    sentence_end +=1
    context = passage[sentence_start:sentence_end]
        
    return context 
