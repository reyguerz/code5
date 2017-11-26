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
	#model.ConstraintInitialBatCharge = Constraint(rule = Equations.Initialize_BatCharge)
	model.ConstraintBatCharge = Constraint(model.TimeSteps, rule = Equations.Update_BatCharge)
	model.ConstraintBatChargeMin = Constraint(model.TimeSteps, rule = Equations.Limit_BatChargeMin)
	model.ConstraintBatChargeMax = Constraint(model.TimeSteps, rule = Equations.Limit_BatChargeMax)



