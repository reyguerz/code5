__author__ = 'Rey Guerrero'

'''
MILP Model of a Microgrid Optimization
version 1. 2017-11


'''

from pyomo.environ import ConcreteModel
from ImportModelInfo import Import_Model_Info
from BuildModel import Build_Model
from SolveShowResults import Solve_Show_Results

def main():

	# for runtime computation
	from datetime import datetime
	starttime = datetime.now()

	#******** START CODE PROPER *********#
	
	model = ConcreteModel() # create instance of model

	print('[1/3]Fetching Input Data, Populating model parameters, Defining Variables...')
	Import_Model_Info(model) # import data and define model  set, parameters and variables

	print('[2/3]Defining Objective function/s and setting the constraints...')
	Build_Model(model) # define constraints and objective function

	print('[3/3]Solving the model...')
	Solve_Show_Results(model) # solve model

	
	#******** END CODE PROPER *********#

	# run time computation and end of program
	stoptime = datetime.now()

	print ('\nruntime: ',stoptime - starttime)
	print('Done! Good luck! \nPress Enter to Exit Program')
	ExitEnter = input()


if __name__ == '__main__':		# this is needed for Python multiprocessing to work in Windows 
	print('Initializing... Importing necessary modules...')
	main()
