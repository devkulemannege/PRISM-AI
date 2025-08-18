from sentence_transformers import SentenceTransformer, util

def identifyRepliedMSg(llmMsgs, customerMsg):
    '''identifies the message which the customer
    replies to using pre-trained models'''
    scores = []
    formattedScores = []
    model = SentenceTransformer(modelName := 'all-MiniLM-L6-v2') # initialize sentence transformer model
    print(f'SBERT Model Used: {modelName}')

    # encode data / vectorize
    cusMsgEncode = model.encode(customerMsg)
    llmMsgEncode = model.encode(llmMsgs)

    # identify replied msg using cosin sim
    for msg in llmMsgEncode: scores.append(util.cos_sim(cusMsgEncode, msg))
    for score in scores: formattedScores.append(score.squeeze().item()) # convert to raw list & extract raw values (float)
    print(f'Cosine Similarity Scores: {formattedScores}') # print scores for debugging purposes
    return llmMsgs[formattedScores.index(max(formattedScores))] # return the msg with the highest similarity

'''
aiList = ["Hi! Don’t miss our Black Friday 30% discount on all Intel i7 laptops.",
          "Hello! We’re offering 20% off on all bread products this weekend.",
          "Join us this Saturday for a PC maintenance workshop — learn to fix your graphic card issues!"]

customer = "Can I get 2 loaves of brown bread with the offer?"
print(identifyRepliedMSg(aiList, customer))
'''