#/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import threading
from random import randint
import time

print ("Starting threaded Pi Server")

#This thread listens for a client and stops when data is received from it.
class Send_Receive_Thread (threading.Thread):
	def __init__(self, threadID, name, server_socket, size, stop_event):
		threading.Thread.__init__(self)
		self.threadid = threadID
		self.name = name
		self.server_socket = server_socket
		self.stop_event = stop_event
		
	def run(self):
		recvData = ''
		#Accept data from the client until some is actually received, then terminate the 
		while not self.stop_event.is_set():
			client, address = self.server_socket.accept()
			data = client.recv(size)
			if data:
				client.send(data)
				self.stop_event.set()
				client.close()
		
#This class quotes Monty Python at you at a rate of 1 quote/second until stop_event is_set(). It will not stop on its own.
class Python_Thread (threading.Thread):
	def __init__(self, threadID, name, stop_event):
		threading.Thread.__init__(self)
		self.threadid = threadID
		self.name = name
		self.stop_event = stop_event
		
	def run(self):
		count = 0
		pyquotes = ["Obstetrician 1: Get the EEG, the BP monitor, and the AVV. \nObstetrician 2: And get the machine that goes 'ping!'. \nObstetrician 1: And get the most expensive machine - in case the Administrator comes.",
					"Dad: The mill's closed. There's no more work. We're destitute. I've got no option but to sell you all for scientific experiments. \n[The children protest and cry] \nDad: That's the way it is my loves. Blame the Catholic Church for not letting me wear one of those little rubber things. Oh, they've done some wonderful things in their time. They preserved the might and majesty, even the mystery, of the Church of Rome, the sanctity of the sacrament, and the indivisible oneness of the Trinity. But if they'd let me wear one of those little rubber things on the end of my cock, we wouldn't be in the mess we are now.", 
					"Hindu, Taoist, Mormon spill theirs just anywhere \nBut God loves those who treat their semen with more care.",
					"Today I think I'll have a French Tickler, for I am a Protestant.", 
					"O Lord! Ooh, you are so big! So absolutely huge. Gosh, we're all really impressed down here, I can tell you.", 
					"O Lord, please don't burn us. \nDon't grill or toast your flock. \nDon't put us on the barbecue \nOr simmer us in stock. \nDon't braise or bake or boil us, \nOr stir-fry us in a wok.", 
					"Ainsworth: During the night old Perkins had his leg bitten sort of... off. \nDr. Livingstone: Eh? Been in the wars, have we? Well, let's take a look at this one leg of yours. Yes... Yes, well, this is nothing to worry about. \nPerkins: Oh, good. \nDr. Livingstone: There's a lot of it about — probably a virus. Keep warm, plenty of rest, and if you're playing any football try and favour the other leg.", 
					"Here is better than home, eh, sir? I mean, at home if you kill someone they arrest you — here they'll give you a gun and show you what to do, sir. I mean, I killed fifteen of those buggers. Now, at home they'd hang me — here they'll give me a fucking medal, sir!"
					"Peasant: Oh, she turned me into a newt!\nBedevere: A newt?\nPeasant: Well, I got better.",
					"You don't frighten us, English pig-dogs! Go and boil your bottoms, sons of a silly person! I blow my nose at you, so-called Ah-thoor Keeng, you and all your silly English K-n-n-n-n-n-n-n-niggits!",
					"Go away or I shall taunt you a second time!",
					"On second thoughts, let's not go to Camelot. It is a silly place.",
					"What... is the air-speed velocity of an unladen swallow?",
					"Now, you listen here: 'e's not the Messiah, 'e's a very naughty boy! Now, go away!",
					"All right, but apart from the sanitation, the medicine, education, wine, public order, irrigation, roads, the fresh-water system, and public health, what have the Romans ever done for us?",
					"Man: I think it was, \"Blessed are the cheesemakers\"!\nGregory's wife: What's so special about the cheesemakers?\nGregory: Well, obviously it's not meant to be taken literally. It refers to any manufacturer of dairy products.",
					"Centurion: What's this then? 'Romanes eunt domus'? 'People called Romanes, they go the 'ouse'?\nBrian: It — it says 'Romans go home'.\nCenturion: No it doesn't. What's Latin for 'Roman'? [Brian hesitates.] Come on, come on!\nBrian: 'Romanus'?\nCenturion: Goes like...?\nBrian: 'Annus'?\nCenturion: Vocative plural of 'annus' is...?\nBrian: 'Anni.'\nCenturion: [writing] 'Romani'. 'Eunt'? What is 'eunt'?\nBrian: 'Go'.\nCenturion: Conjugate the verb 'to go'.\nBrian: Ire, eo, is, it, imus, itis, eunt.\nCenturion: So 'eunt' is...?\nBrian: Third person plural, present indicative. 'They go'.\nCenturion: But 'Romans go home' is an order, so you must use the...?\nBrian: [getting his earlock pulled, increasingly panicked] Eeeh, imperative!\nCenturion: Which is…?\nBrian: Uh, uhm, 'ii'! 'Ii'!\nCenturion: How many Romans?\nBrian: Aah! Plural, plural! 'Ite'! 'Ite'!\nCenturion: [writing] 'Ite'. 'Domus'? Nominative? 'Go home', this is motion towards, isn't it, boy?\nBrian: Dative! [centurion draws his sword and holds it to Brian's throat] Ah! Not dative! Not the dative! Aah! Accusative, accusative! 'Domum', sir, 'ad domum'.\nCenturion: Except that 'domus' takes the...?\nBrian: The locative, sir!\nCenturion: Which is...?\nBrian: 'Domum'!\nCenturion: 'Domum'. [writing] 'Um'. Understand?\nBrian: Yes, sir.\nCenturion: Now write it out a 'undred times.\nBrian: Yes, thank you Sir, Hail Caesar. [calming down]\nCenturion: Hail Caesar. If it's not done by sunrise, I'll cut your balls off.\n[At sunrise the wall is covered in writing.]\nBrian: [exhausted, finishing the last line] Finished!\nCenturion: Right. Now don't do it again.",
					"Brian: ...Will you please listen? I'm not the Messiah! Do you understand? Honestly!\nWoman: Only the true Messiah denies his divinity!\nBrian: What? Well, what sort of chance does that give me? All right, I am the Messiah!\nCrowd: He is! He is the Messiah!\nBrian: Now, fuck off!\nArthur: How shall we fuck off, oh Lord?",
					"I will not have my fwiends widiculed by the common soldiewy. Anybody else feel like a little giggle when I mention my fwiend Biggus Dickus? What about you? Do you find it wisible when I say the name 'Biggus Dickus'? He has a wife, you know. You know what she's called? She's called 'Incontinentia'. 'Incontinentia Buttocks'"
					"No. 1: The Larch. The Larch. The Larch.",
					"is it a stockbroker? Is it a quantity Surveyor? Is it a church warden? NO! It's Bicycle Repair Man!",
					"Colonel: Watkins, why did you join the army?\nWatkins: For the water-skiing and the travel, sir. Not for the killing, sir. I asked them to put it on my form, sir: \"no killing\".\nColonel: Watkins, are you a pacifist?\nWatkins: No, sir. I'm not a pacifist, sir: I'm a coward.",
					"I must warn you, sir, that outside I have police dog Josephine, who is not only armed and trained to sniff out certain substances but is also a junkie.",
					"I'm a lumberjack and I'm OK, I sleep all night and I work all day.\nI cut down trees, I eat my lunch, I go to the lavatory. On Wednesdays I'll go shopping, and have buttered scones for tea.\nI cut down trees, I skip and jump, I like to press wildflowers. I put own womens' clothing, and hang around in bars.\nI cut down trees, I wear high heels, suspenders, and a bra. I wish I'd been a girlie, just like my dear Mama!",
					"This man, he doesn't know when he's beaten! He doesn't know when he's winning, either. He has no… sort of… sensory apparatus…",
					"This is a vegetarian restaurant — we serve no meat of any kind. We're not only proud of that, we're smug about it.'",
					"Interviewer: Was there anything unusual about Dinsdale?\nWoman: Certainly not! He was perfectly normal in every way! Except... inasmuch as he thought he was being followed by a giant hedgehog named Spiny Norman.",
					"Nobody expects the Spanish Inquisition!",
					"Mr. Wiggin: This is a 12-story block combining classical neo-Georgian features with the efficiency of modern techniques. The tenants arrive here and are carried along the corridor on a conveyor belt in extreme comfort, past murals depicting Mediterranean scenes, towards the rotating knives. The last twenty feet of the corridor are heavily soundproofed. The blood pours down these chutes and the mangled flesh slurps into these...\nClient 1: Excuse me.\nMr. Wiggin: Yes?\nClient 1: Did you say 'knives'?\nMr. Wiggin: Rotating knives, yes.\nClient 2: Do I take it that you are proposing to slaughter our tenants?\nMr. Wiggin: ...Does that not fit in with your plans?",
					"Man: Good morning, I'd care to purchase a chicken, please.\nVendor: Don't come here with that posh talk, you nasty, stuck-up twit!\nMan: I beg your pardon?\nVendor: A chicken, sir? Certainly. Here we are.\nMan: Thank you. And how much does that come to per pound, my good fellow?\nVendor: Per pound, you slimy trollop? What kind of a ponce are you?\nMan: I'm sorry?\nVendor: Four and six a pound, sir. Nice and ready for roasting.\nMan: I see. And I'd care to purchase some stuffing in addition, please.\nVendor: Use your own, you great poofy poll-nagger!\nMan: What?\nVendor: Certainly, sir, some stuffing.\nMan: Oh, thank you.\nVendor: Oh, \"thank you\", says the great queen, like a la-di-da pooftah!\nMan: I beg your pardon?\nVendor: That's alright, sir, call again!\mMan: Excuse me...\nVendor: What is it now, you great pillock?!\nMan: I can't help but notice that you insult me, and then you're polite to me, alternately.\nVendor: Oh, I'm terribly sorry to hear that, sir!\nMan: Oh, that's all right. It doesn't really matter.\nVendor: Tough titty if it did, you nasty, spotted prancer!",
					"I love animals, that's why I like to kill 'em.",
					"Rule 1 — no pooftahs. Rule 2 — no member of the faculty is to maltreat the abos in any way whatsoever if there's anyone watching. Rule 3 — no pooftahs. Rule 4 — I don't want to catch any of you not drinking after lights out. Rule 5 — no pooftahs. Rule 6 — there is NO Rule 6. Rule 7 — no pooftahs!",
					"I AM NOT A LOONY! Why should I be tarred with the epithet \"loony\" merely because I have a pet halibut? I've heard tell that Sir Gerald Nabarro has a pet prawn called Simon, and you wouldn't call Sir Gerald a loony, would you? Furthermore, Dawn Pelforth, the lady show jumper, had a clam called Sir Stefford after the late Chancellor, Allen Bullock has two pikes, both called Norman, and the late, great Marcel Proust had a haddock! If you're calling the author of À la recherche du temps perdu a loony, I shall have to ask you to step outside!",
					"We at the Church of the Divine Loony believe in the power of prayer to turn the face purple!",
					"Well, I've been in the city for 30 years and I've never once regretted being a nasty, greedy, cold-hearted, avaricious money-grubber... er, Conservative!",
					
					]
		while not self.stop_event.is_set():
			print pyquotes[randint(0, len(pyquotes) - 1)]
			print "\n"
			time.sleep(1)
    	
    	
def set_up_socket():
	host = ''
	port = 20533
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind((host,port))
	server_socket.listen(1)
	return server_socket

server_socket = set_up_socket()
stop_event = threading.Event()
py_thread = Python_Thread(1, 'thread 1', stop_event)
size = 1024
server_thread = Send_Receive_Thread(2, 'thread 2', server_socket, size, stop_event)

py_thread.run()
server_thread.run()

"""
def main():
	
	return 0

if __name__ == '__main__':
	main()
"""
