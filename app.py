from datasets import load_dataset
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
import os
import psycopg2

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

@st.cache(suppress_st_warning=True)
def get_qa_pair_low(file, rand):
	df = pd.read_csv(file, sep="\t", lineterminator='\n')
	a = df.sample(1).reset_index()
	st.text(df)
	return {
		"text": a["text"][0],
		"question": a["question"][0],
		"answer": a["answer\r"][0]
	}

@st.cache(suppress_st_warning=True)
def get_qa_pair_mid(file, rand):
	df = pd.read_csv(file,sep="\t", lineterminator='\n')
	a = df.sample(1).reset_index()
	return {
		"text": a["text"][0],
		"question": a["question"][0],
		"answer": a["answer\r"][0]
	}

@st.cache(suppress_st_warning=True)
def get_qa_pair_high(file, rand):
	df = pd.read_csv(file,sep="\t", lineterminator='\n')
	a = df.sample(1).reset_index()
	return {
		"text": a["text"][0],
		"question": a["question"][0],
		"answer": a["answer\r"][0]
	}

@st.cache(suppress_st_warning=True)
def getmcq(rand):
	df = pd.read_csv("mcq.tsv",sep="\t", lineterminator='\n')
	a = df.sample(1).reset_index()
	ind = df.keys()
	return {
		"question": a[ind[0]][0],
		"real_ans": a[ind[1]][0],
		"conf_ans": a[ind[2]][0]
	}

# DB  Functions
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()


def check_hashes(password, hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False

conn = psycopg2.connect('postgres://vjnsllyatxtnin:34fa0fecfe8a62314d80c24743557d38ce558ed372598cbf5229fc867abe8be6@ec2-50-19-160-40.compute-1.amazonaws.com:5432/d96bve3gfgrvgg', sslmode='require')
c = conn.cursor()

def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY, fullname TEXT, password TEXT)')

def create_stats_table():
	c.execute('CREATE TABLE IF NOT EXISTS stats_table(username TEXT PRIMARY KEY, comprehension_score DOUBLE PRECISION DEFAULT 0.0, synonyms_score INTEGER DEFAULT 0, app_usage_score INTEGER DEFAULT 0, overall_score INTEGER DEFAULT 0)')

def add_userdata(username, fullname, password):
	try:
		c.execute('INSERT INTO userstable(username, fullname,password) VALUES (%s,%s,%s)', (username, fullname, password))
		conn.commit()
	except:
		st.text("Unable to add value in database, as username already exists.")

def add_statsdata(username):
	c.execute('INSERT INTO stats_table(username, comprehension_score, synonyms_score, app_usage_score, overall_score) VALUES (%s,%s,%s,%s,%s)', (username, 0.0, 0, 0, 0))
	conn.commit()

def check_username(username):
	c.execute("SELECT * FROM userstable WHERE username = %s", (username,))
	data = c.rowcount
	return data

def login_user(username, password):
	c.execute('SELECT * FROM userstable WHERE username = %s AND password = %s', (username, password))
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

def get_comprehension_score():
	c.execute('SELECT comprehension_score FROM stats_table where username = %s', (st.session_state['username'],))
	data = c.fetchall().pop()[0]
	return data

def update_comprehension_score(score):
	c.execute('UPDATE stats_table set comprehension_score = %s, overall_score = overall_score + 1 where username = %s',(score, st.session_state['username']))
	conn.commit()

def update_synonym_score():
	c.execute('UPDATE stats_table set synonyms_score = synonyms_score + 1, overall_score = overall_score + 1 where username = %s', (st.session_state['username'],))
	conn.commit()

def update_usage_score():
	c.execute('UPDATE stats_table set app_usage_score = app_usage_score + 1, overall_score = overall_score + 1 where username = %s', (st.session_state['username'],))
	conn.commit()

def get_leaderboard():
	c.execute('SELECT * FROM stats_table order by overall_score DESC')
	data = c.fetchall()
	return data

def drive_basic_login():
	st.sidebar.image("angrezzi.jpeg")
	menu = ["Login", "SignUp"]
	choice = st.sidebar.selectbox("Menu", menu)

	if choice == "Login":
		username = st.sidebar.text_input("User Name")
		password = st.sidebar.text_input("Password", type='password')
		if st.sidebar.checkbox("Login"):
			create_usertable()
			hashed_pswd = make_hashes(password)

			result = login_user(username, check_hashes(password, hashed_pswd))
			#fullname = get_user_fullname(username, check_hashes(password, hashed_pswd))
			admin = is_admin_user(username, password)
			if result:
				st.session_state['username'] = username
				st.success("Hi {}".format(username))
			else:
				st.warning("Incorrect Username/Password")
			return result, admin

	elif choice == "SignUp":
		st.subheader("Create New Account")
		fullname = st.text_input("Full Name")
		new_user = st.text_input("Username")
		new_password = st.text_input("Password", type='password')

		if st.button("Signup"):
			create_usertable()
			create_stats_table()
			row_count = check_username(new_user)
			if row_count == 0:
				add_userdata(new_user, fullname, make_hashes(new_password))
				add_statsdata(new_user)
				st.success("You have successfully created a valid account")
				st.info("Go to Login Menu to login")
			else :
				st.warning("This username already exists. Any other username which comes to your mind?")

	return False,False

def main():
	result, is_admin = drive_basic_login()

	if result:
		scoreM = 0
		score = 0
		"""Adaptive Education"""

		# authentication logic + get which class student belongs to : high, mid, low
		stud_class = "low"
		if is_admin:
			option = st.radio(
		 'Choose anything you want to practise!',
		 ("Reading Comprehension", "Translate to Hindi", "Translate to English", "Synonyms", "View User Details", "View Leader Board"))
		else :
			option = st.radio(
		 'Choose anything you want to practise!',
		 ("Reading Comprehension", "Translate to Hindi", "Translate to English","Synonyms"))

		st.write('You selected:', option)

		if option == "Reading Comprehension":
			st.title("Reading Comprehension")
			st.text("Question Number : " + str(state.question_number))
			comprehension_score = get_comprehension_score()
			st.text("Your Score : " + str(comprehension_score))

			if comprehension_score <= 5.0:
				cqa = get_qa_pair_low("low.tsv", state.question_number)
			elif comprehension_score > 5.0 and comprehension_score <= 15.0 :
				cqa = get_qa_pair_mid("high.tsv", state.question_number)
			else :
				cqa = get_qa_pair_high("high.tsv", state.question_number)

			st.subheader("Context : ")
			st.markdown(cqa['text'])

			st.subheader("Question : ")
			st.markdown(cqa['question'])

			message1 = st.text_area("Enter your answer")
			# a = st.selectbox('Answer:', ["Please select an answer","Confirm Answer"])
			# a = st.radio("Confirm : ", ["Answering","Confirm!"])

			# if a != "Answering":
			if st.button("Check"):
				st.subheader("Your Answer :")
				st.text(message1)
				score = 0
				if fuzz.ratio(message1.lower(), cqa["answer"].lower()) > 75:
					score = fuzz.ratio(message1.lower(), cqa["answer"].lower())
				if score > 0 :
					new_score = comprehension_score + score
					update_comprehension_score(new_score)
				st.text("Score : " + str(score))
				# if score:
				# 	st.text("Correct!")
				# 	st.subheader("Full Answer : ")
				# 	st.text(cqa['answer'])
				# else:
				# 	st.text("Incorrect!")
				# 	st.subheader("Actual Answer : ")
				# 	st.text(cqa['answer'])

				# writing to score.tsv
				fp = open("score.tsv", "a")
				fp.write(cqa["text"].strip() + "\t" + cqa["question"].strip() + "\t" + cqa[
					"answer"].strip() + "\t" + message1.strip() + "\t" + str(score) + "\n")
				fp.close()

			if st.button("Show Answers"):
				try:
					df = pd.read_csv("score.tsv", sep="\t")
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
				state.question_number += 1
				scoreM += score

		elif option == 'Translate to Hindi':
			update_usage_score()
			txt = st.text_area("Enter here to Translate", "Type Here")
			out = translator.translate(txt, dest="hi")
			st.subheader("Hindi Text : " + out.text)

		elif option == "Translate to English":
			update_usage_score()
			txt2 = st.text_area("Enter here to Translate", "Type Here")
			out2 = translator.translate(txt2, dest="en")
			st.subheader("Hindi Text : " + out2.text)

		elif option == 'View User Details':
			user_result = view_all_users()
			user_details = pd.DataFrame(user_result, columns=["Username", "FullName", "Password"])
			st.dataframe(user_details)

		elif option == 'View Leader Board':
			stats_table = get_leaderboard()
			stats_details = pd.DataFrame(stats_table, columns=["Username", "Comprehensions", "Synonyms", "Usage", "Overall Score"])
			st.dataframe(stats_details)

		else:
			q = getmcq(state.question_number)
			st.text("What is the same meaning word for " + q["question"] + "?")
			real_ans = q["real_ans"]
			conf_ans = q["conf_ans"].split(",")
			conf_ans.append(real_ans)
			x = st.radio("Options : ", conf_ans)

			if st.button("Check"):
				if x == real_ans:
					st.text("Correct!")
					update_synonym_score()
				else:
					st.text("Incorrect!")
					st.text("Correct Answer: " + real_ans)

			if st.button("Next Question"):
				state.question_number += 1

		# 	if st.checkbox("Paraphrase Given Sentence"):
		# 		txt2 = st.text_area("Enter here to Paraphrase","Type Here")
		# 		out2 = translator.translate(txt2,dest="hi")
		# 		st.json(out2)

		st.sidebar.subheader("About This App")
		st.sidebar.write(
			"#Integrating AI and differentiated Data across student buckets, this is an attempt at using AI tools to enable English Language acquisition amongst a focussed group of 94 kids of a TFI classroom. ")
		st.sidebar.info(
			"The app is meant for the use of students and Teach For India Fellows of Grade 8, Holy Mother English School; Mumbai.")
		st.sidebar.subheader("Created with ♥ ")
		st.sidebar.text("By Debamita, Abhilash, Honey, & Nishant")

if __name__ == '__main__':
	main()
