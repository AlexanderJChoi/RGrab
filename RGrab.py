import praw

c_secret=""
c_id=""
user_agent=""
with open(".client_secret", "r") as f:
	c_secret = f.read().splitlines()[0]
with open(".client_id", "r") as f:
    c_id = f.read().splitlines()[0]
with open(".user_agent", "r") as f:
    user_agent = f.read().splitlines()[0]
    

reddit = praw.Reddit(
	client_id=c_id,
	client_secret=c_secret,
	user_agent=user_agent
)


url = input("Please enter the link for the reddit comments you want to grab")
submission = reddit.submission(url=url)

submission.comments.replace_more(limit=None)
outfile = input("Please enter the name of the file you want the comments out put to. Use _ in place of spaces.")
counter = 0
with open(outfile, "w") as f:
	for comment in submission.comments.list():
		f.write(" == BEGIN COMMENT == \n")
		f.write(comment.body)
		f.write("\n == END COMMENT == \n")
		counter+=1
	f.write(f"Output {counter} comments")

print(f"Output {counter} comments to file {outfile}")
