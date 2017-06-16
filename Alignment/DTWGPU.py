import pycuda.autoinit
import pycuda.driver as drv
import pycuda.gpuarray as gpuarray
import pycuda.cumath
import numpy as np
import matplotlib.pyplot as plt
import time
import scipy.io as sio
import pkg_resources
import sys
from Alignments import *
from AlignmentTools import *
import _SequenceAlignment as SAC

from pycuda.compiler import SourceModule

DTW_ = None
DTWSSM_ = None
getSumSquares_ = None
finishCSM_ = None

def getResourceString(filename):
    if 'Alignment' not in sys.modules:
        #If calling from within this directory
        fin = open(filename)
        s = fin.read()
        fin.close()
    else:
        #If calling from imported package
        s = pkg_resources.resource_string('Alignment', '/%s'%filename)
    return s

def initParallelAlgorithms():
    global DTW_
    global DTWSSM_
    
    s = getResourceString("DTWGPU.cu")
    mod = SourceModule(s)
    DTW_ = mod.get_function("DTW")

    s = getResourceString("DTWSSMGPU.cu")
    mod = SourceModule(s)
    DTWSSM_ = mod.get_function("DTWSSM")

def roundUpPow2(x):
    return np.array(int(2**np.ceil(np.log2(float(x)))), dtype=np.int32)

def doDTWGPU(CSM, ci, cj):
    #Minimum dimension of array can be at max size 1024
    #for this scheme to fit in memory
    M = CSM.shape[0]
    N = CSM.shape[1]

    diagLen = np.array(min(M, N), dtype = np.int32)
    diagLenPow2 = roundUpPow2(diagLen)
    NThreads = min(diagLen, 512)
    res = gpuarray.to_gpu(np.array([0.0], dtype=np.float32))
    M = np.array(M, dtype=np.int32)
    N = np.array(N, dtype=np.int32)
    ci = np.array(ci, dtype = np.int32)
    cj = np.array(cj, dtype = np.int32)
    DTW_(CSM, M, N, ci, cj, diagLen, diagLenPow2, res, block=(int(NThreads), 1, 1), grid=(1, 1), shared=12*diagLen)
    ret = res.get()[0]
    return ret

def doIBDTWGPU(SSMA, SSMB, returnCSM = False, printElapsedTime = False):
    """
    :param SSMA: MxM self-similarity matrix of first curve (gpuarray)
    :param SSMB: NxN self-similarity matrix of second curve (gpuarray)
    :param returnCSM: If True, return the CSM.  If false, just return the final cost
    :param printElapsedTime: Print the elapsed time
    """
    M = SSMA.shape[0]
    N = SSMB.shape[0]

    CSM = np.zeros((M, N), dtype=np.float32)
    CSM = gpuarray.to_gpu(CSM)

    diagLen = np.array(min(M, N), dtype = np.int32)
    diagLenPow2 = roundUpPow2(diagLen)
    NThreads = min(diagLen, 512)

    M = np.array(M, dtype=np.int32)
    N = np.array(N, dtype=np.int32)
    tic = time.time()

    DTWSSM_(SSMA, SSMB, CSM, M, N, diagLen, diagLenPow2, block=(int(NThreads), 1, 1), grid=(int(M), int(N)), shared=12*diagLen)
    if returnCSM:
        return CSM.get()
    else:
        res = doDTWGPU(CSM, 0, 0)
        if printElapsedTime:
            print "Elapsed Time GPU: ", time.time() - tic
        return res

if __name__ == '__main__':
    initParallelAlgorithms()
    t1 = np.linspace(0, 1, 500)
    t1 = np.sqrt(t1)
    t2 = np.linspace(0, 1, 500)
    ci = 100
    cj = 20
    #t2 = np.sqrt(t2)
    #t1 = t1**2

    X = np.zeros((len(t1), 2))
    X[:, 0] = t1
    X[:, 1] = np.cos(4*np.pi*t1) + t1
    Y = np.zeros((len(t2), 2))
    Y[:, 0] = t2
    Y[:, 1] = np.cos(4*np.pi*t2) + t2 + 0.5

    tic = time.time()
    (DCPU, CSM, backpointers, involved) = constrainedDTW(X, Y, lambda x,y: np.sqrt(np.sum((np.array(x, dtype=np.float32)-np.array(y, dtype=np.float32))**2)), ci, cj)
    # print "Elapsed Time Python: ", time.time() - tic
    # DCPU = DCPU[1::, 1::]
    resPython = DCPU[-1, -1]
    CSM = getCSM(X, Y)

    tic = time.time()
    resC = SAC.constrainedDTW(CSM, ci, cj)
    print "Elapsed Time C: ", time.time() - tic

    CSM = np.array(CSM, dtype = np.float32)
    CSM = gpuarray.to_gpu(CSM)
    resGPU = doDTWGPU(CSM, ci, cj)


    print "Python Result: %g"%resPython
    print "C Result: %g"%resC
    print "GPU Result: %g"%resGPU