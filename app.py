from datasets import load_dataset
import streamlit as st
import pandas as pd 
from googletrans import Translator 
import session_state
import time 
from fuzzywuzzy import fuzz,process

# import torch
# from transformers import PegasusForConditionalGeneration, PegasusTokenizer

state = session_state.get(question_number=0)
score = session_state.get(score=0)
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
	a = df.sample().reset_index()
	return {
	"text" : a["text"][0],
	"question" : a["question"][0],
	"answer" : a["answer\r"][0]
	}



def main():
	"""Adaptive Education"""
	st.title("Reading Comprehension with AI capabilities")

	#normal RC

	# authentication logic + get which class student belongs to : high, mid, low 
	stud_class = "high" 

	option = st.selectbox(
     'What would you like to do?',
     ('Reading Comprehension', 'Translate to Hindi', 'Translate to English'))

	st.write('You selected:', option)
 
	if option == "Reading Comprehension":
		st.text("Question Number : " +str(state.question_number))
		cqa = get_qa_pair(stud_class+".tsv",state.question_number) # high.tsv is saved


		st.subheader("Context : ")
		st.markdown(cqa['text'])

		st.subheader("Question : ")
		st.markdown(cqa['question'])	

		message1 = st.text_area("Enter your answer","")
		a = st.selectbox('Answer:', ["Please select an answer","Confirm Answer"])

		if a != "Please select an answer":
			st.subheader("Your Answer : ")
			st.text(message1)
			score = 0
			if fuzz.ratio(message1.lower(),cqa["answer"].lower()) > 75:
				score = fuzz.ratio(message1.lower(),cqa["answer"].lower()) 
			st.text("Score : "+str(score))
			if score:
				st.text("Correct!")
				st.subheader("Full Answer : ")
				st.text(cqa['answer'])
			else: 
				st.text("Incorrect!")
				st.subheader("Actual Answer : ")
				st.text(cqa['answer'])
		
		
		if st.button("Get New Question"):
			state.question_number+=1

	elif option == 'Translate to Hindi':
		txt = st.text_area("Enter here to Translate","Type Here")
		out = translator.translate(txt,dest="hi")
		st.subheader("Hindi Text : "+out.text)
	else: 
		txt2 = st.text_area("Enter here to Translate","Type Here")
		out2 = translator.translate(txt2,dest="en")
		st.subheader("Hindi Text : "+out2.text)
	
# 	if st.checkbox("Paraphrase Given Sentence"):
# 		txt2 = st.text_area("Enter here to Paraphrase","Type Here")
# 		out2 = translator.translate(txt2,dest="hi")
# 		st.json(out2)


	st.sidebar.subheader("About This App")
	st.sidebar.write("#Integrating AI and differentiated Data across student buckets, this is an attempt at using AI tools to enable English Language acquisition amongst a focussed group of 93 kids of a TFI classroom. ")
	st.sidebar.info("The app is meant for the use of students and Teach For India Fellows of Grade 8, Holy Mother English School, Mumbai.")
	st.sidebar.subheader("Created with ♥ by: ")
	st.sidebar.text("Debamita Samajdar, Abhilash Paul, and Honey Joshi.")




if __name__ == '__main__':
	main()	
