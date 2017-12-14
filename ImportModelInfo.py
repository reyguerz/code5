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

	

	DictStorageCostPerYearR = {}
	StorageInterestRate = 0.0375				# reference [13]
	StoragePresentCost = 0.830					# accessed online 2 Dec 2017, Powerwall price, wikipedia. USD / Wh = 0.470

	DictCostStorages = { 'bat' : StoragePresentCost } # accessed online 2 Dec 2017, Powerwall price, wikipedia
	
	'''
	# Storage Cost per Year for every timestep considering interest rate
	for i in range(len(ListStorages)):
		for j in range(NumOfTimeSteps):
			CostPerYear = StoragePresentCost / ( 1 + StorageInterestRate)**(math.floor((NumOfTimeSteps+2)/8760))		# per year computation of NPC, assuming hourly timesteps. NOTE: wrong code here for NumOfTimeSteps
			dictdummy = { (ListStorages[i],ListTimeSteps[j]) : CostPerYear }
			DictStorageCostPerYear.update(dictdummy)

			outfile.write(str(ListStorages[i]) + ',' + str(j)+','+str(CostPerYear)+',\n') # for code testing purposes only
	'''

	# Storage Cost per Year for every year considering interest rate
	NumOfYears = 10
	ListYearStepsR = [ i+1 for i in range(NumOfYears-1)]	# number of years + 1. Meant for battery replacement after the first year.
	print(ListYearStepsR)
	for i in range(len(ListStorages)):
		for j in range(NumOfYears-1):
			CostPerYear = StoragePresentCost / ( ( 1 + StorageInterestRate)**(j+1) )		# per year computation of NPC, assuming yearly timesteps. except on the first year which has a differenet/separate variable
			dictdummy = { (ListStorages[i],ListYearStepsR[j]) : CostPerYear }
			DictStorageCostPerYearR.update(dictdummy)

			outfile.write(str(ListStorages[i]) + ',' + str(j)+','+str(CostPerYear)+',\n') # for code testing purposes only
		

	ValBigMaxBatSize = 100000000					# max battery capacity. used in LP constraints to linearize nonlinear function/term

	'''
	MaxBatReplacements = 5						# max number of times that the battery is replaced
	ListBatReplacements = [i+1 for i in range(MaxBatReplacements)]
	DictBatReplacements = {}
	for i in range(MaxBatReplacements):
			dictdummy = {ListBatReplacements[i] : i+1}
			DictBatReplacements.update(dictdummy)
	'''

	#ValBatCap2MaxThroughput = 3960				# method from [2017 Bordin], values from [2017 Alsaidan] for Li-Ion Batteries = 3960
	#ValValBatCap2MaxThroughput here are test values
	#ValBatCap2MaxThroughput = 5				
	ValBatCap2MaxThroughput = 840

	ValBigMaxBatThroughput = 1000000000000		# maximum through put. used in LP constraints to linearize nonlinear function/term

	#******** PYOMO CODE PROPER *********#



	#******** SETS *******#  #define sets or indices of the parameters and variables
	model.Microsources = Set(initialize = ListMicrosources, ordered = True)
	model.Storages = Set(initialize = ListStorages, ordered = True )
	model.TimeSteps = Set(initialize = ListTimeSteps, ordered = True )
	model.YearStepsR = Set(initialize = ListYearStepsR, ordered = True)
	#model.BatReplacements = Set(initialize = ListBatReplacements, ordered = True)


	#******* PARAMETERS ********#	# define parameters or the given values of the problem
	model.NumOfTimeSteps = Param(initialize = NumOfTimeSteps)
	model.CostMicrosources = Param(model.Microsources, initialize = DictCostMicrosources)
	model.OutMicrosources = Param(model.Microsources, model.TimeSteps, initialize = DictOutMicrosources)
	
	model.Demand = Param(model.TimeSteps, initialize = DictDemand)
	model.EquivalentLossFactorLimit = Param(initialize = EquivalentLossFactorLimit)

	
	#*** Battery Specs and Parameters
	model.CostStorages = Param(model.Storages, initialize = DictCostStorages)
	model.StorageCostPerYear = Param(model.Storages, model.YearStepsR, initialize = DictStorageCostPerYearR)
	model.BigMaxBatSize = Param(initialize = ValBigMaxBatSize)

	model.InitialSOC = Param(initialize = ValInitialSOC)
	model.MinSOC = Param(initialize = ValMinSOC)
	model.MaxSOC = Param(initialize = ValMaxSOC)
	model.BatChargeEff = Param(initialize = ValBatChargeEff)
	model.BatDisChargeEff = Param(initialize = ValBatDisChargeEff)
	model.BatCharge2CapRatio = Param(initialize = ValBatCharge2CapRatio)
	model.BatDischarge2CapRatio = Param(initialize = ValBatDischarge2CapRatio)

	#model.BatMaxThroughputMultiplier = Param(model.BatReplacements, initialize = DictBatReplacements)
	model.BatCap2MaxThroughput = Param (initialize = ValBatCap2MaxThroughput)

	#model.BigMaxBatThroughput = Param(initialize = ValBigMaxBatThroughput)

	#******* VARIABLES ********# # define the variable/s to solve
	#** NOTE: Bounds can be declared properly and orderly in the separate module/file
	model.SizeMicrosources = Var(model.Microsources, domain = NonNegativeIntegers, bounds = (0,10000)) #* 10GW max
	model.SizeStorages = Var(model.Storages, domain = NonNegativeIntegers, bounds = (0,100000000)) #* 100MWh capacity	
	model.LoadNotServed = Var(model.TimeSteps, domain = NonNegativeReals)
	
	#*** Battery Related Variables
	model.StorageOut = Var(model.Storages, model.TimeSteps, domain = NonNegativeReals, bounds = (0,100000000)) #* 100MWh capacity
	model.StorageIn = Var(model.Storages, model.TimeSteps, domain = NonNegativeReals, bounds = (0,100000000)) #* 100MWh capacity
	model.BatCharge = Var(model.Storages, model.TimeSteps, domain = NonNegativeReals, bounds = (0,100000000)) #* 100MWh capacity
	
	
	# * Battery Replacement Variables
	model.SizeStoragesR = Var(model.Storages, model.YearStepsR, domain = NonNegativeIntegers, bounds = (0,100000000)) #* 100MWh capacity	
	model.uTime2Replace = Var(model.Storages, model.YearStepsR, domain = NonNegativeIntegers, bounds = (0,1)) # as defined in the constraints, the value will always be 0 or 1
	

	'''
	model.wStorageSizeCost = Var(model.Storages,model.YearSteps, domain = NonNegativeReals)
	model.uTime2Replace = Var(model.YearSteps, domain = NonNegativeReals, bounds = (0,1)) # as defined in the constraints, the value will always be 0 or 1
	model.uFlagBatMaxThroughput = Var(model.BatReplacements, model.YearSteps, domain = Binary)
	model.SumStorageOut = Var(model.YearSteps, domain = NonNegativeReals)
	model.BatMaxThroughput = Var(model.Storages, domain = NonNegativeReals)
	model.wSumStorageOut = Var(model.BatReplacements, model.YearSteps, domain = NonNegativeReals)
	model.wBatMaxThroughput = Var(model.BatReplacements, model.YearSteps, domain = NonNegativeReals)
	'''