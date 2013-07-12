##file: profiling_functions.py
from fipy import Grid1D, CellVariable, TransientTerm, DiffusionTerm, Viewer
import cProfile
import pstats 
import os
import numpy as np
import matplotlib.pyplot as plt
import math
import inspect
import matplotlib.gridspec as gridspec
from fipyprofile import FiPyProfile
import datetime

class FiPyProfileTime(FiPyProfile):
    def __init__(self, runfunc, ncells, regenerate=False, funcString=None):
        self.runfunc = runfunc
        self.ncells = ncells
        self.regenerate = regenerate
        self.funcString = funcString
        for ncell in ncells:
            if not os.path.exists(self.datafilestring(ncell)) or self.regenerate:
                self.profile(ncell)

    def datafilestring(self, ncell):
        return "{funcString}{ncell}.stats".format(funcString=self.funcString, ncell=ncell)
	# now = datetime.datetime.now() 
        # year = now.year
        # month = now.month
        # day = now.day
        # hour = now.hour

        # dateString = "{month}-{day}-{year}_{hour}.stats".format(month=month, day=day, year=year, hour=hour)
        # return dateString
	#return str({now})[:16].replace(" ", "_")).stats.format(now=now)
	
    def profile(self, ncell):
        print ncell,
        runFuncString = 'self.runfunc(ncell={ncell})'.format(ncell=ncell)
        cProfile.runctx(runFuncString, globals(), locals(), filename=self.datafilestring(ncell))
        
    def get_stats(self, ncell):
        return pstats.Stats(self.datafilestring(ncell))

    def get_sorted_keys(self, ncell, sort_field="cumulative"):
        sorted_stats = self.get_stats(ncell).sort_stats(sort_field)
        return sorted_stats.fcn_list

    
    def get_time_for_function(self, function_key, ncell, index=3):
        """index = 3 refers to cumulative time"""
        stats =  self.get_stats(ncell).stats
        if function_key in stats:
            return stats[function_key][index]
        else:
            return np.nan

    @staticmethod
    def get_key_from_function_pointer(function_pointer):
        return (inspect.getfile(function_pointer), inspect.getsourcelines(function_pointer)[1], function_pointer.func_name)

    def plot(self, keys, field="cumulative", doFullProfile = True, shortLabel = True):
        stats = self.get_stats(self.ncells[0])
        sort_args = stats.get_sort_arg_defs()[field]
        index = sort_args[0][0][0]
        
        fig = plt.figure()
        gs = gridspec.GridSpec(2,1)
        ax1 = plt.subplot(gs[1, :-1])

      
        for key in keys:
            functionTimes = []
            for ncell in self.ncells:
                print ncell,
                functionTimes.append(self.get_time_for_function(key, ncell, index))
            if key[0] == '~':
                label = key[2]
            else:
                if shortLabel:
                    fileName = os.path.split(key[0])[1]
                else:
                    fileName = key[0]
                label = fileName + ": " + key[2]

            label = r""+str(label).replace("_", "\_").replace("<", "$<$").replace(">", "$>$")
            ax1.loglog(self.ncells, functionTimes, label = label)
            print key[0], key[2]
            
        if doFullProfile:
            allTimes = []
            runfunc_key = self.get_key_from_function_pointer(self.runfunc)
            for ncell in self.ncells:
                print ncell,
                allTimes.append(self.get_time_for_function(runfunc_key, ncell))
            ax1.loglog(self.ncells, allTimes, label = "full profile")        

        plt.ylabel(sort_args[1])
        plt.xlabel("ncells")
      
        gs.tight_layout(fig, rect=[0,0,1,1])
        plt.loglog(self.ncells, self.ncells**2, label="$ncells^2$")
        plt.loglog(self.ncells, self.ncells*np.log(self.ncells), label="$n\log(n)$")
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, ncol=1, mode="wrap", borderaxespad=0., prop={'size': 12})
        plt.show() 
      #  plt.savefig("Polyxtal_5_slowest.png")


     



