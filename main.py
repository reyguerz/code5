__author__ = 'Rey Guerrero'

'''
MILP Model of a Microgrid Optimization
version 1. 2017-11


'''

from pyomo.environ import ConcreteModel
from  ImportModelInfo import Import_Model_Info
from BuildModel import Build_Model
from SolveShowResults import Solve_Show_Results

def main():
	
	model = ConcreteModel() # create instance of model

	Import_Model_Info(model) # import data and define model  set, parameters and variables

	Build_Model(model) # define constraints and objective function

	Solve_Show_Results(model) # solve model

	print('\nDone! Good luck! \nPress Enter to Exit Program')
	ExitEnter = input()



if __name__ == '__main__':		# this is needed for Python multiprocessing to work in Windows 
	main()
