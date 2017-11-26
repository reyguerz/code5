__author__ = 'Rey Guerrero'

'''
MILP Model of a Microgrid Optimization



import data and define model  set, parameters and variables


'''

# code below is for testing overall program structure

from pyomo.environ import Set, Param, Var, NonNegativeIntegers, NonNegativeReals
from AdminFunctions import Read_List_CSV_File
from Component import Solar_PV_Out, Wind_TB_Out


def Import_Model_Info(model):
	

	#******** CODE TO GET MODEL INFO, CAN BE FROM OTHER SOURCES/ DATABASE *********#
	# NOTE: This can still be optimized and be more flexible and readable

	Irradiance = []
	WindSpeed = []
	Temperature = []
	Demand = []

	# extract 
	infilename = 'input\PV' + '.csv'
	Read_List_CSV_File(infilename, Irradiance)

	infilename = 'input\WindSpeed' + '.csv'
	Read_List_CSV_File(infilename, WindSpeed)
	
	infilename = 'input\Temperature' + '.csv'
	Read_List_CSV_File(infilename, Temperature)
	
	infilename = 'input\Demand' + '.csv'
	Read_List_CSV_File(infilename, Demand)


	ListMicrosources = ['pv','wt']
	ListStorages = ['bat']
	DictCostMicrosources = { 
		'pv' : 2420,
		'wt' : 2500,
	}
	DictCostStorages = { 'bat' : 830 }

	NumOfTimeSteps = len (Irradiance) # assumption that RE and load have the same period of data
	ListTimeSteps = [ i+1 for i in range(NumOfTimeSteps)]

	outfilename ='output\IntermediateParam.csv' # for code testing purposes only
	outfile = open(outfilename,'w') # for code testing purposes only
	
	DictOutMicrosources = {}
	for i in range(len(ListMicrosources)):
		for j in range(NumOfTimeSteps):
			EnergyOut = 0
			if ListMicrosources[i] == 'pv':
				EnergyOut = Solar_PV_Out(Irradiance[j], Temperature[j])
			elif ListMicrosources[i] == 'wt':
				EnergyOut = Wind_TB_Out(WindSpeed[j])

			outfile.write(str(ListMicrosources[i]) + ',' + str(j)+','+str(EnergyOut)+',\n') # for code testing purposes only
			
			dictdummy = { (ListMicrosources[i],ListTimeSteps[j]) : EnergyOut}
			DictOutMicrosources.update(dictdummy)
			



	DictDemand = {}
	for i in range(NumOfTimeSteps):
		DictDemand.update({ListTimeSteps[i] : Demand[i]})

	ValInitialSOC = 0.50
	ValMinSOC = 0.20
	ValMaxSOC = 1.00

	#******** PYOMO CODE PROPER *********#



	#******** SETS *******#  #define sets or indices of the parameters and variables
	model.Microsources = Set(initialize = ListMicrosources, ordered = True)
	model.Storages = Set(initialize = ListStorages, ordered = True )
	model.TimeSteps = Set(initialize = ListTimeSteps, ordered = True )


	#******* PARAMETERS ********#	# define parameters or the given values of the problem
	model.CostMicrosources = Param(model.Microsources, initialize = DictCostMicrosources)
	model.CostStorages = Param(model.Storages, initialize = DictCostStorages)
	model.OutMicrosources = Param(model.Microsources, model.TimeSteps, initialize = DictOutMicrosources)
	model.Demand = Param(model.TimeSteps, initialize = DictDemand)
	model.InitialSOC = Param(initialize = ValInitialSOC)
	model.MinSOC = Param(initialize = ValMinSOC)
	model.MaxSOC = Param(initialize = ValMaxSOC)

	#******* VARIABLES ********# # define the variable/s to solve
	model.SizeMicrosources = Var(model.Microsources, domain = NonNegativeIntegers)
	model.SizeStorages = Var(model.Storages, domain = NonNegativeIntegers)	
	model.StorageOut = Var(model.TimeSteps, domain = NonNegativeReals)
	model.StorageIn = Var(model.TimeSteps, domain = NonNegativeReals)
	model.BatCharge = Var(model.TimeSteps, domain = NonNegativeReals)