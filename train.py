import gym 
import itertools 
import numpy as np 
import sys 
from collections import defaultdict 

  



class simuser(object):

	def __init__(self):
		self.states = ['FOOD_TYPE_FILLED', 'PRICE_FILLED', 'LOCATION_FILLED', 'FOOD_TYPE_CONF', 'PRICE_CONF', 'LOCATION_CONF']
		self.actions = ['REQUEST_FOOD_TYPE', 'REQUEST_PRICE', 'REQUEST_LOCATION', 'EXPLICIT_CONFIRM_FOOD_TYPE', 'EXPLICIT_CONFIRM_PRICE', 'EXPLICIT_CONFIRM_LOCATION']
		self.actionsMap = {}
		self.reward = 0
		self.stateDict = {}
		for i in range(len(self.actions)):
			self.actionsMap[self.actions[i]] = self.states[i] 


	def reset(self):
		for i in self.states:
			self.stateDict[i] = False
		self.reward = 0
		return self.stringify()

	def stringify(self):
		s = ''
		for i in self.stateDict:
			s += i + '=' + str(self.stateDict[i]) + ','
		return s


	def step(self, action):
		action = self.actions[action]

		reward = -5
		if(self.stateDict[self.actionsMap[action]] == False):
			if('EXPLICIT_CONFIRM' in action):
				x = action.replace('EXPLICIT_CONFIRM_', '') + '_FILLED'
				if(self.stateDict[x] == True):
					self.stateDict[self.actionsMap[action]] = True
			else:
				self.stateDict[self.actionsMap[action]] = True


		nextState = self.stringify()

		isDone = all(self.stateDict.values())
		if(isDone):
			reward += 500
		return (nextState, reward, isDone)


actions = ['REQUEST_FOOD_TYPE', 'REQUEST_PRICE', 'REQUEST_LOCATION', 'EXPLICIT_CONFIRM_FOOD_TYPE', 'EXPLICIT_CONFIRM_PRICE', 'EXPLICIT_CONFIRM_LOCATION']
class QAgentTrain(object):

	def __init__(self):
		self.Q = defaultdict(lambda: np.zeros(6) )

	def createEpsilonGreedyPolicy(self, epsilon, num_actions): 
		def policyFunction(state): 

			Action_probabilities = np.ones(num_actions, 
					dtype = float) * epsilon / num_actions 
					
			best_action = np.argmax(self.Q[state]) 
			Action_probabilities[best_action] += (1.0 - epsilon) 
			return Action_probabilities 

		return policyFunction 




	def qLearning(self, env, num_episodes, discount_factor = 0.99, 
								alpha = 1, epsilon = 0.2): 
		
		# state -> (action -> action-value). 
	 
		
		# Create an epsilon greedy policy function 
		# appropriately for environment action space 
		policy = self.createEpsilonGreedyPolicy( epsilon, 6) 
		reward_str = ''
		rewards = []
		# For every episode 
		episodic_reward = 0
		for ith_episode in range(num_episodes): 
			if(ith_episode > 0 and ith_episode % 9 == 0 ):
				epsilon -= 0.02
			# Reset the environment and pick the first action 
			state = env.reset() 
			action_count = 0
			alpha = 1/(1+ith_episode)
			episodic_reward = 0
			for t in itertools.count(): 
				
				# get probabilities of all actions from current state 
				action_probabilities = policy(state) 
				# choose action according to 
				# the probability distribution 

				action = np.random.choice(np.arange( 
						len(action_probabilities)), 
						p = action_probabilities) 

				# take action and get reward, transit to next state 
				next_state, reward, done = env.step(action) 
				episodic_reward += reward
				# TD Update 
				best_next_action = np.argmax(self.Q[next_state])	 
				td_target = reward + discount_factor * self.Q[next_state][best_next_action] 
				td_delta = td_target - self.Q[state][action] 
				self.Q[state][action] += (alpha) * td_delta 
				action_count += 1
				# done is True if episode terminated 
				if done or action_count >= 20: 
					break
					
				state = next_state 
			rewards.append(episodic_reward)
			reward_str  += str(ith_episode) + ',' + str(episodic_reward) + '\n'

		return (self.Q, reward_str) 
	def train(self):
		env = simuser()
		(Q, reward_str) = self.qLearning(env, 100) 
		text_file = open("rewards.csv", "w")
		text_file.write(reward_str)
		text_file.close()
		return Q
		

tmp = QAgentTrain()
Q = tmp.train()
states = ['FOOD_TYPE_FILLED', 'PRICE_FILLED', 'LOCATION_FILLED', 'FOOD_TYPE_CONF', 'PRICE_CONF', 'LOCATION_CONF']
sar = ''
for i in Q:
	sar += i + actions[np.argmax(Q[i])] + '\n'
text_file = open("policy.txt", "w")
text_file.write(sar)
text_file.close()
