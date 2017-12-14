__author__ = 'Rey Guerrero'

'''
MILP Model of a Microgrid Optimization


define constraints and objective function

'''

import Equations
from pyomo.environ import Objective, Constraint, minimize

def Build_Model(model):

	#******** OBJECTIVE FUNCTION *******#
	model.OBJ = Objective(rule=Equations.Compute_NPC, sense = minimize)


	#******** CONSTRAINTS ********#
	model.ConstraintEnergyBalance = Constraint(model.TimeSteps, rule = Equations.Balance_Energy)
	model.ConstraintEquivalentLossFactorLimit = Constraint(rule = Equations.Limit_EquivalentLossFactor)

	
	#*** Battery-Related Constraints
	model.ConstraintBatCharge = Constraint(model.Storages, model.TimeSteps, rule = Equations.Update_BatCharge)
	model.ConstraintBatChargeMin = Constraint(model.Storages, model.TimeSteps, rule = Equations.Limit_BatChargeMin)
	model.ConstraintBatChargeMax = Constraint(model.Storages, model.TimeSteps, rule = Equations.Limit_BatChargeMax)
	model.ConstraintMaxStorageOut = Constraint(model.Storages, model.TimeSteps, rule = Equations.Limit_StorageOut)
	model.ConstraintMaxStorageIn = Constraint(model.Storages, model.TimeSteps, rule = Equations.Limit_StorageIn)
	
	#* Battery Replacement Constraints
	model.ConstraintSumSOYear1 = Constraint(model.Storages, rule = Equations.Limit_SumSOYear1)
	model.ConstraintSumSOYear2Horizon = Constraint(model.Storages, model.YearStepsR, rule = Equations.Limit_SumSOYear2Horizon)
	model.ConstraintStorageReplacement1 = Constraint(model.Storages, model.YearStepsR, rule = Equations.Limit_StorageReplacement1)
	model.ConstraintStorageReplacement2 = Constraint(model.Storages, model.YearStepsR, rule = Equations.Limit_StorageReplacement2)
	model.ConstraintStorageReplacement3 = Constraint(model.Storages, model.YearStepsR, rule = Equations.Limit_StorageReplacement3)


	'''
	model.ConstraintWStorageSizeCost1 = Constraint(model.Storages, model.YearSteps, rule = Equations.Limit_StorageSizeCost1)
	model.ConstraintWStorageSizeCost2 = Constraint(model.Storages, model.YearSteps, rule = Equations.Limit_StorageSizeCost2)
	model.ConstraintWStorageSizeCost3 = Constraint(model.Storages, model.YearSteps, rule = Equations.Limit_StorageSizeCost3)
	model.ConstraintUTime2Replace = Constraint(model.YearSteps, rule = Equations.Define_uTime2Replace)
	model.ConstraintSumStorage = Constraint(model.YearSteps, rule = Equations.Define_SumStorageOut)
	model.ConstraintBatMaxThroughput = Constraint(model.Storages, rule = Equations.Define_BatMaxThroughput)
	model.ConstraintWBatMaxThroughput1 = Constraint(model.BatReplacements, model.YearSteps, rule = Equations.Limit_BatMaxThroughput1)
	model.ConstraintWBatMaxThroughput2 = Constraint(model.Storages, model.BatReplacements, model.YearSteps, rule = Equations.Limit_BatMaxThroughput2)
	model.ConstraintWBatMaxThroughput3 = Constraint(model.BatReplacements, model.YearSteps, rule = Equations.Limit_BatMaxThroughput3)
	model.ConstraintWBatMaxThroughput4 = Constraint(model.Storages, model.BatReplacements, model.YearSteps, rule = Equations.Limit_BatMaxThroughput4)
	model.ConstraintWSumStorageOut1 = Constraint(model.Storages, model.BatReplacements, model.YearSteps, rule = Equations.Limit_SumStorageOut1)
	model.ConstraintWSumStorageOut2 = Constraint(model.BatReplacements, model.YearSteps, rule = Equations.Limit_SumStorageOut2)
	model.ConstraintWSumStorageOut3 = Constraint(model.BatReplacements, model.YearSteps, rule = Equations.Limit_SumStorageOut3)
	model.ConstraintWSumStorageOut4 = Constraint(model.BatReplacements, model.YearSteps, rule = Equations.Limit_SumStorageOut4)
	'''
	


