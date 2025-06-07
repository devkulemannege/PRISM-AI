from reply_selector import identifyRepliedMSg


customerMsg = input("Enter a customer message: ")

result = identifyRepliedMSg(customerMsg, faiss_index_path="Master\campaign_vector.index", meta_path="Master\campaign_vector.")
print("Most relevant LLM message:", result)


