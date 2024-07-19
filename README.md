**FLow of project**

1. The ‘owner’ and the ‘repo’ is taken input from the user, 

2. API fetches the versions for that particular git repo

3. Display the versions list to user

4. User chooses from the version list, ‘base_version’ and ‘compare_version’

5. User inputs a ‘query’ and ‘n’ i.e. number of PRs to be displayed, and a radio input that whether the user wants to view the results of only Sentence Transformer models(i.e. LLM) or just GPT or both. 

6. Get all the commits data from the compare versions API

7. Use that data to get the PR numbers in the first 500 characters by matching the pattern for each commit and get all the details of each PR(i.e. Number, title, body, labels)from another API, and sort them according to the pr number.

8. Send this data to individual models(sentence transformers), embed the PR data and the query, and find the similarity

9. Append the similarity scores of all models to one json file and calculate the average of all the models and sort according to that.

10. If Only LLM is selected by the user, simply display the top n results to user.

11. If Both are selected then give a few top results to chatGPT and print the results of chatGPT to the frontend(this option acts as a RAG Model)  

12. If only GPT is selected, then pass all the PR data to GPT, either iteratively or batch depending on the token limit, and display the results in proper format to the frontend.



**Steps Followed:**

**1. Data Preparation**
    concatenate the title, body, and labels for each PR into a single text string.

**2. Embedding**
    use a pre-trained embedding model such as sentence-transformers to embed these text strings.(e.g. 'all-MiniLM-L6-v2')

**3. Similarity Search**
    use a similarity search algorithm like cosine similarity to find the most relevant PRs.

**4. GPT Evaluation**
    send the most relevant PRs to the GPT model for further refinement.




![Data_Collection](https://github.com/user-attachments/assets/af244304-c1dc-4cf2-b7e2-912892ec6056)

![Data_Processing](https://github.com/user-attachments/assets/0f96408a-74f5-4bff-9772-9f241d60c19f)

![Interface(1)](https://github.com/user-attachments/assets/5d2247b4-ba12-4429-9255-7181263cd4c2)

![Interface(2)](https://github.com/user-attachments/assets/60f753f8-ef2e-4283-a2fa-762f78fea11a)



