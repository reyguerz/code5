__author__ = 'Rey Guerrero'

'''
MILP Model of a Microgrid Optimization



import data and define model  set, parameters and variables


'''

# code below is for testing overall program structure
import math
import VarList

from pyomo.environ import Set, Param, Var, NonNegativeIntegers, NonNegativeReals, Binary
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
	
	NumOfTimeSteps = len (Irradiance) # assumption that RE and load have the same period of data
	ListTimeSteps = [ i+1 for i in range(NumOfTimeSteps)]

	outfilename ='output\IntermediateParam.csv' # for code testing purposes only
	outfile = open(outfilename,'w') # for code testing purposes only
	
	DictOutMicrosources = {}
	for i in range(len(ListMicrosources)):
		for j in range(NumOfTimeSteps):
			EnergyOut = 0
			if ListMicrosources[i] == 'pv':
				EnergyOut = Solar_PV_Out(Irradiance[j], Temperature[j], j)
			elif ListMicrosources[i] == 'wt':
				EnergyOut = Wind_TB_Out(WindSpeed[j], j)

			outfile.write(str(ListMicrosources[i]) + ',' + str(j)+','+str(EnergyOut)+',\n') # for code testing purposes only
			
			dictdummy = { (ListMicrosources[i],ListTimeSteps[j]) : EnergyOut}
			DictOutMicrosources.update(dictdummy)
			



	DictDemand = {}
	for i in range(NumOfTimeSteps):
		DictDemand.update({ListTimeSteps[i] : Demand[i]})

	
	EquivalentLossFactorLimit = 0.01

	#** Battery Specs and Parameters

	ValInitialSOC = VarList.BatInitialSOC 
	ValMinSOC = 0.20
	ValMaxSOC = 1.00
	ValBatChargeEff = VarList.BatChEff 			# charging efficiency
	ValBatDisChargeEff = VarList.BatDisChEff 	# discharging efficiency
	ValBatCharge2CapRatio = 5/13				# initial data. from Powerwall specs of 5kW continuous output
	ValBatDischarge2CapRatio = 5/13

	DictCostStorages = { 'bat' : 0.470 } # accessed online 2 Dec 2017, Powerwall price, wikipedia

	DictStorageCostPerYear = {}
	StorageInterestRate = 0.0375				# reference [13]
	StoragePresentCost = 0.470					# accessed online 2 Dec 2017, Powerwall price, wikipedia. USD / Wh

	for i in range(len(ListStorages)):
		for j in range(NumOfTimeSteps):
			CostPerYear = StoragePresentCost / ( 1 + StorageInterestRate)**(math.floor((NumOfTimeSteps+2)/8760))		# per year computation of NPC, assuming hourly timesteps
			dictdummy = { (ListStorages[i],ListTimeSteps[j]) : CostPerYear }
			DictStorageCostPerYear.update(dictdummy)

			outfile.write(str(ListStorages[i]) + ',' + str(j)+','+str(CostPerYear)+',\n') # for code testing purposes only


	BigMaxBatSize = 100000000					# max battery capacity. used in LP constraints to linearize nonlinear function/term

	MaxBatReplacements = 20						# max number of times that the battery is replaced
	ListBatReplacements = [i+1 for i in range(MaxBatReplacements)]
	DictBatReplacements = {}
	for i in range(MaxBatReplacements):
			dictdummy = {ListBatReplacements[i] : i+1}
			DictBatReplacements.update(dictdummy)

	ValBatCap2MaxThroughput = 3960				# method from [2017 Bordin], values from [2017 Alsaidan] for Li-Ion Batteries
	ValBigMaxBatThroughput = 1000000000000		# maximum through put. used in LP constraints to linearize nonlinear function/term

	#******** PYOMO CODE PROPER *********#



	#******** SETS *******#  #define sets or indices of the parameters and variables
	model.Microsources = Set(initialize = ListMicrosources, ordered = True)
	model.Storages = Set(initialize = ListStorages, ordered = True )
	model.TimeSteps = Set(initialize = ListTimeSteps, ordered = True )
	model.BatReplacements = Set(initialize = ListBatReplacements, ordered = True)


	#******* PARAMETERS ********#	# define parameters or the given values of the problem
	model.NumOfTimeSteps = Param(initialize = NumOfTimeSteps)
	model.CostMicrosources = Param(model.Microsources, initialize = DictCostMicrosources)
	model.OutMicrosources = Param(model.Microsources, model.TimeSteps, initialize = DictOutMicrosources)
	
	model.Demand = Param(model.TimeSteps, initialize = DictDemand)
	model.EquivalentLossFactorLimit = Param(initialize = EquivalentLossFactorLimit)

	
	#*** Battery Specs and Parameters
	model.CostStorages = Param(model.Storages, initialize = DictCostStorages)
	model.StorageCostPerYear = Param(model.Storages, model.TimeSteps, initialize = DictStorageCostPerYear)
	model.BigMaxBatSize = Param(initialize = BigMaxBatSize)

	model.InitialSOC = Param(initialize = ValInitialSOC)
	model.MinSOC = Param(initialize = ValMinSOC)
	model.MaxSOC = Param(initialize = ValMaxSOC)
	model.BatChargeEff = Param(initialize = ValBatChargeEff)
	model.BatDisChargeEff = Param(initialize = ValBatDisChargeEff)
	model.BatCharge2CapRatio = Param(initialize = ValBatCharge2CapRatio)
	model.BatDischarge2CapRatio = Param(initialize = ValBatDischarge2CapRatio)

	model.BatMaxThroughputMultiplier = Param(model.BatReplacements, initialize = DictBatReplacements)
	model.BatCap2MaxThroughput = Param (initialize = ValBatCap2MaxThroughput)
	model.BigMaxBatThroughput = Param(initialize = ValBigMaxBatThroughput)

	#******* VARIABLES ********# # define the variable/s to solve
	model.SizeMicrosources = Var(model.Microsources, domain = NonNegativeIntegers)
	model.SizeStorages = Var(model.Storages, domain = NonNegativeIntegers)	

	model.LoadNotServed = Var(model.TimeSteps, domain = NonNegativeReals)
	
	#*** Battery Related Variables
	model.StorageOut = Var(model.TimeSteps, domain = NonNegativeReals)
	model.StorageIn = Var(model.TimeSteps, domain = NonNegativeReals)
	model.BatCharge = Var(model.TimeSteps, domain = NonNegativeReals)
	
	'''
	# * Battery Replacement Variables
	model.wStorageSizeCost = Var(model.Storages,model.TimeSteps, domain = NonNegativeReals)
	model.uTime2Replace = Var(model.TimeSteps, domain = Binary)
	model.uFlagBatMaxThroughput = Var(model.BatReplacements, model.TimeSteps, domain = Binary)
	model.SumStorageOut = Var(model.TimeSteps, domain = NonNegativeReals)
	model.BatMaxThroughput = Var(model.Storages, domain = NonNegativeReals)
	model.wSumStorageOut = Var(model.BatReplacements, model.TimeSteps, domain = NonNegativeReals)
	model.wBatMaxThroughput = Var(model.BatReplacements, model.TimeSteps, domain = NonNegativeReals)
	'''