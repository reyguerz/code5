__author__ = 'Rey Guerrero'

'''
MILP Model of a Microgrid Optimization


Equations or expressions to be used as objective function and constraints

'''

def Compute_NPC(model):
	return sum(model.SizeMicrosources[i]*model.CostMicrosources[i] for i in model.Microsources) + sum(model.SizeStorages[j]*model.CostStorages[j] for j in model.Storages)

def Balance_Energy(model, TimeSteps):
	return sum(model.SizeMicrosources[i]*model.OutMicrosources[i,TimeSteps] for i in model.Microsources) + model.StorageOut[TimeSteps] - model.StorageIn[TimeSteps] >= model.Demand[TimeSteps]

def Update_BatCharge(model, TimeSteps):
	if TimeSteps == 1:
		return model.BatCharge[TimeSteps] == model.InitialSOC * model.SizeStorages[model.Storages[1]]
	if TimeSteps > 1:
		return model.BatCharge[TimeSteps] == model.BatCharge[TimeSteps - 1] + model.StorageIn[TimeSteps] - model.StorageOut[TimeSteps]

def Limit_BatChargeMin(model, TimeSteps):
	return model.BatCharge[TimeSteps] >= model.MinSOC * model.SizeStorages[model.Storages[1]]

def Limit_BatChargeMax(model, TimeSteps):
	return model.BatCharge[TimeSteps] <= model.MaxSOC * model.SizeStorages[model.Storages[1]]