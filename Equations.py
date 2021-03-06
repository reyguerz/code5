__author__ = 'Rey Guerrero'

'''
MILP Model of a Microgrid Optimization


Equations or expressions to be used as objective function and constraints

'''

#******* Objective Function/s *******#


# NPC with no battery replacement
def Compute_NPC(model):
	return sum(model.SizeMicrosources[i]*model.CostMicrosources[i] for i in model.Microsources) + sum( ( model.SizeStorages[j]*model.CostStorages[j] ) for j in model.Storages)

#NPC with battery replacement
#def Compute_NPC(model):
#	return sum(model.SizeMicrosources[i]*model.CostMicrosources[i] for i in model.Microsources) + sum( ( sum(model.StorageCostPerYear[j,t] * model.wStorageSizeCost[j,t] for t in model.TimeSteps) ) for j in model.Storages)



#******* Energy Balance and Demand Requirements*******#


#def Balance_Energy(model, TimeSteps):
#	return sum(model.SizeMicrosources[i]*model.OutMicrosources[i,TimeSteps] for i in model.Microsources) + model.StorageOut[TimeSteps] - model.StorageIn[TimeSteps] >= model.Demand[TimeSteps]

def Balance_Energy(model, TimeSteps):
	return sum(model.SizeMicrosources[i]*model.OutMicrosources[i,TimeSteps] for i in model.Microsources) + model.StorageOut[TimeSteps] - model.StorageIn[TimeSteps] + model.LoadNotServed[TimeSteps] >= model.Demand[TimeSteps]

def Limit_EquivalentLossFactor(model):
	return (1 / model.NumOfTimeSteps) * sum((model.LoadNotServed[i] / model.Demand[i]) for i in model.TimeSteps) <= model.EquivalentLossFactorLimit


#******* Battery Constraints *******#
def Update_BatCharge(model, TimeSteps):
	if TimeSteps == 1:
		return model.BatCharge[TimeSteps] == model.InitialSOC * model.SizeStorages[model.Storages[1]]
	if TimeSteps > 1:
		return model.BatCharge[TimeSteps] == model.BatCharge[TimeSteps - 1] + model.BatChargeEff * model.StorageIn[TimeSteps] - (1/model.BatDisChargeEff) * model.StorageOut[TimeSteps]

def Limit_BatChargeMin(model, TimeSteps):
	return model.BatCharge[TimeSteps] >= model.MinSOC * model.SizeStorages[model.Storages[1]]

def Limit_BatChargeMax(model, TimeSteps):
	return model.BatCharge[TimeSteps] <= model.MaxSOC * model.SizeStorages[model.Storages[1]]

def Limit_StorageOut(model, TimeSteps):
	return model.StorageOut[TimeSteps] <= model.BatDischarge2CapRatio * model.SizeStorages[model.Storages[1]]

def Limit_StorageIn(model, TimeSteps):
	return model.StorageIn[TimeSteps] <= model.BatCharge2CapRatio * model.SizeStorages[model.Storages[1]]
	

#* Battery Replacement Constraints

def Limit_StorageSizeCost1(model, Storages, TimeSteps):
	return model.wStorageSizeCost[Storages,TimeSteps] <= model.uTime2Replace[TimeSteps] * model.BigMaxBatSize

def Limit_StorageSizeCost2(model, Storages, TimeSteps):
	return model.wStorageSizeCost[Storages,TimeSteps] <= model.SizeStorages[Storages]

def Limit_StorageSizeCost3(model, Storages, TimeSteps):
	return model.wStorageSizeCost[Storages,TimeSteps] >= model.BigMaxBatSize * (model.uTime2Replace[TimeSteps] - 1) + model.SizeStorages[Storages]

def Define_uTime2Replace(model, TimeSteps):
	if TimeSteps == 1:
		return model.uTime2Replace[TimeSteps] == 1
	if TimeSteps > 1:
		return model.uTime2Replace[TimeSteps] == sum( model.uFlagBatMaxThroughput[r,TimeSteps] - model.uFlagBatMaxThroughput[r,TimeSteps - 1] for r in model.BatReplacements)

def Define_SumStorageOut(model, TimeSteps):
	return model.SumStorageOut[TimeSteps] == sum( model.StorageOut[t+1] for t in range(TimeSteps)) # TAKE NOTE OF THIS CODE. MAY CAUSE A BUG DEPENDING ON PROPER PYTHON/PYOMO SYNTAX

def Define_BatMaxThroughput(model, Storages):
	return model.BatMaxThroughput[Storages] == model.SizeStorages[model.Storages[1]] * model. BatCap2MaxThroughput

def Limit_SumStorageOut1(model, Storages, BatReplacements, TimeSteps):
	return model.SumStorageOut[TimeSteps] - model.wSumStorageOut[BatReplacements,TimeSteps] <= model.BatMaxThroughputMultiplier[BatReplacements] * model.BatMaxThroughput[Storages]

def Limit_SumStorageOut2(model, BatReplacements, TimeSteps):
	return model.wSumStorageOut[BatReplacements,TimeSteps] <= model.SumStorageOut[TimeSteps]

def Limit_SumStorageOut3(model, BatReplacements, TimeSteps):
	return model.wSumStorageOut[BatReplacements,TimeSteps] <= model.BigMaxBatThroughput * model.uFlagBatMaxThroughput[BatReplacements,TimeSteps]

def Limit_SumStorageOut4(model, BatReplacements, TimeSteps):
	return model.wSumStorageOut[BatReplacements,TimeSteps] >= model.BigMaxBatThroughput * (model.uFlagBatMaxThroughput[BatReplacements,TimeSteps] - 1) + model.SumStorageOut[TimeSteps]

def Limit_BatMaxThroughput1(model, BatReplacements, TimeSteps):
	return model.SumStorageOut[TimeSteps] >= model.BatMaxThroughputMultiplier[BatReplacements] * model.wBatMaxThroughput[BatReplacements,TimeSteps]

def Limit_BatMaxThroughput2(model, Storages, BatReplacements, TimeSteps):
	return model.wBatMaxThroughput[BatReplacements,TimeSteps] <= model.BatMaxThroughput[Storages]

def Limit_BatMaxThroughput3(model, BatReplacements, TimeSteps):
	return model.wBatMaxThroughput[BatReplacements,TimeSteps] <= model.BigMaxBatThroughput * model.uFlagBatMaxThroughput[BatReplacements,TimeSteps]

def Limit_BatMaxThroughput4(model, Storages, BatReplacements, TimeSteps):
	return model.wBatMaxThroughput[BatReplacements,TimeSteps] >= model.BigMaxBatThroughput * (model.uFlagBatMaxThroughput[BatReplacements,TimeSteps] - 1) + model.BatMaxThroughput[Storages]
