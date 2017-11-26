__author__ = 'Rey Guerrero'

'''
MILP Model of a Microgrid Optimization

Solve and Display/Show Results


'''
from pyomo.opt import SolverFactory
from pyomo.core import Var, Param, IntegerSet
import pyomo.environ


def Solve_Show_Results(model):

	def pyomo_postprocess(options=None, instance=None, results=None):
 		model.SizeMicrosources.display()
 		model.SizeStorages.display()
	
	opt = SolverFactory("glpk")
	results = opt.solve(model)
	results.write()
	print("\nDisplaying Solution\n" + '-'*60)
	pyomo_postprocess(None, model, results)

	outfilename = 'output\Results.csv'
	outfile = open(outfilename, 'w')

	outfile.write('objective' + str(model.OBJ.value) + ',\n')
	for val in model.component_objects(Var, active=True):
		varobject = getattr(model,str(val))
		for index in varobject:
			outfile.write(str(val) + ',' + str(index) + ',' + str(varobject[index].value) + ',\n')
	'''
	for val in model.component_objects(Param, active=True):
		varobject = getattr(model,str(val))
		if isinstance(varobject.domain, IntegerSet):
			for index in varobject:
				outfile.write(str(val) + ',' + str(index) + ',' + str(varobject[index].value) + ',\n')
		else:
			outfile.write(str(val) + ',' + str(varobject.value) + ',\n')	
	'''
	outfile.close()

