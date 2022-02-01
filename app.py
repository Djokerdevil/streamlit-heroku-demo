import streamlit as st
import pandas as pd 
from googletrans import Translator 
import session_state
import time 
from fuzzywuzzy import fuzz,process
# Security
#passlib,hashlib,bcrypt,scrypt
import hashlib
# DB Management
import sqlite3

# import torch
# from transformers import PegasusForConditionalGeneration, PegasusTokenizer

state = session_state.get(question_number=0)
translator = Translator()


# model_name = 'tuner007/pegasus_paraphrase'
# torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
# tokenizer = PegasusTokenizer.from_pretrained(model_name)
# model = PegasusForConditionalGeneration.from_pretrained(model_name).to(torch_device)

# def get_response(input_text,num_return_sequences,num_beams):
# 	batch = tokenizer([input_text],truncation=True,padding='longest',max_length=60, return_tensors="pt").to(torch_device)
# 	translated = model.generate(**batch,max_length=60,num_beams=num_beams, num_return_sequences=num_return_sequences, temperature=1.5)
# 	tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
# 	return tgt_text

@st.cache
def get_qa_pair(file,rand):
	df = pd.read_csv(file,sep="\t",lineterminator='\n')
	a = df.sample(1).reset_index()
	return {
	"text" : a["text"][0],
	"question" : a["question"][0],
	"answer" : a["answer\r"][0]
	}

@st.cache
def getmcq(rand):
	df = pd.read_csv("mcq.tsv",sep="\t",lineterminator='\n')
	a = df.sample(1).reset_index()
	ind = df.keys()
	return {
	"question" : a[ind[0]][0],
	"real_ans" : a[ind[1]][0],
	"conf_ans" : a[ind[2]][0]
	}


def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()


def check_hashes(password, hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False

conn = sqlite3.connect('data.db')
c = conn.cursor()


# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username, password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (username, password))
	conn.commit()


def login_user(username, password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
	data = c.fetchall()
	return data


def is_admin_user(username, password):
	if username == 'admin' and password == 'cinnamonsabir':
		return True
	else :
		return False


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data


def drive_basic_login():
	menu = ["Login", "SignUp"]
	choice = st.sidebar.selectbox("Menu", menu)

	if choice == "Login":
		username = st.sidebar.text_input("User Name")
		password = st.sidebar.text_input("Password", type='password')
		if st.sidebar.checkbox("Login"):
			create_usertable()
			hashed_pswd = make_hashes(password)

			result = login_user(username, check_hashes(password, hashed_pswd))
			admin = is_admin_user(username, password)
			if result:
				st.success("Logged In as {}".format(username))
			else:
				st.warning("Incorrect Username/Password")
			return result, admin

	elif choice == "SignUp":
		st.subheader("Create New Account")
		new_user = st.text_input("Username")
		new_password = st.text_input("Password", type='password')

		if st.button("Signup"):
			create_usertable()
			add_userdata(new_user, make_hashes(new_password))
			st.success("You have successfully created a valid Account")
			st.info("Go to Login Menu to login")
	return False,False


def main():

	result, is_admin = drive_basic_login()

	if result:

		scoreM = 0
		score = 0

		#normal RC

		# authentication logic + get which class student belongs to : high, mid, low 
		stud_class = "high" 

		if is_admin:
			option = st.radio(
		 'Choose anything you want to practise!',
		 ('Reading Comprehension', 'Translate to Hindi', 'Translate to English',"Synonyms", "View User Details"))		
		else :
			option = st.radio(
		 'Choose anything you want to practise!',
		 ('Reading Comprehension', 'Translate to Hindi', 'Translate to English',"Synonyms"))


		st.write('You selected:', option)
	 
		if option == "Reading Comprehension":
			
			st.title("Reading Comprehension with AI capabilities")
			st.text("Question Number : " +str(state.question_number))
			st.text("Your Score : " +str(scoreM))
			cqa = get_qa_pair(stud_class+".tsv",state.question_number) # high.tsv is saved


			st.subheader("Context : ")
			st.markdown(cqa['text'])

			st.subheader("Question : ")
			st.markdown(cqa['question'])	

			message1 = st.text_area("Enter your answer","Type Here")
			# a = st.selectbox('Answer:', ["Please select an answer","Confirm Answer"])
			# a = st.radio("Confirm : ", ["Answering","Confirm!"])
			
			# if a != "Answering":
			if st.button("Check"):
				st.subheader("Your Answer :")
				st.text(message1)
				score = 0
				if fuzz.ratio(message1.lower(),cqa["answer"].lower()) > 75:
					score = fuzz.ratio(message1.lower(),cqa["answer"].lower()) 
				st.text("Score : "+str(score))
				# if score:
				# 	st.text("Correct!")
				# 	st.subheader("Full Answer : ")
				# 	st.text(cqa['answer'])
				# else: 
				# 	st.text("Incorrect!")
				# 	st.subheader("Actual Answer : ")
				# 	st.text(cqa['answer'])
			
				#writing to score.tsv
				fp = open("score.tsv","a")
				fp.write(cqa["text"].strip()+"\t"+cqa["question"].strip()+"\t"+cqa["answer"].strip()+"\t"+message1.strip()+"\t"+str(score)+"\n")
				fp.close()
				 	
				
			
			if st.button("Show Answers"):
					try:
						df = pd.read_csv("score.tsv",sep="\t")
						json = df.to_json(orient="records")
						# json2 = {}
						# for i in range(len(json["Text"])):
						# 	json2[i] = {}
						
						# for i in range(len(json["Text"])):
						# 	json2[i][]
						
						st.json(json)
					except: 
						st.text("No Questions Answered Yet!")
			if st.button("Get New Question"):
				state.question_number+=1
				scoreM +=score

		elif option == 'Translate to Hindi':
			txt = st.text_area("Enter here to Translate","Type Here")
			out = translator.translate(txt,dest="hi")
			st.subheader("Hindi Text : "+out.text)
		elif option == "Translate to English": 
			txt2 = st.text_area("Enter here to Translate","Type Here")
			out2 = translator.translate(txt2,dest="en")
			st.subheader("Hindi Text : "+out2.text)
		else:
			q = getmcq(state.question_number)
			st.text("Question : Choose the same meaning word "+q["question"]+"?")
			real_ans = q["real_ans"]
			conf_ans = q["conf_ans"].split(",")
			conf_ans.append(real_ans)
			x = st.radio("Select your Answer : ",conf_ans)
			
			
			if st.button("Check"):
				if x == real_ans:
					st.text("Correct!")
				else:
					st.text("Incorrect!")
					st.text("Correct Answer: "+real_ans)

			if st.button("Next Question"):
				state.question_number+=1
				
	# 	if st.checkbox("Paraphrase Given Sentence"):
	# 		txt2 = st.text_area("Enter here to Paraphrase","Type Here")
	# 		out2 = translator.translate(txt2,dest="hi")
	# 		st.json(out2)


	st.sidebar.subheader("About This App")
	st.sidebar.write("#Integrating AI and differentiated Data across student buckets, this is an attempt at using AI tools to enable English Language acquisition amongst a focussed group of 94 kids of a TFI classroom. ")
	st.sidebar.info("The app is meant for the use of students and Teach For India Fellows of Grade 8, Holy Mother English School;Mumbai.")
	st.sidebar.subheader("Created with ♥ ")
	st.sidebar.text("By Debamita, Abhilash, Honey, & Nishant")




if __name__ == '__main__':
	main()	
