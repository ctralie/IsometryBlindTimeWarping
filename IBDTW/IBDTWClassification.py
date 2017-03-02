import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
import sys
sys.path.append('..')
sys.path.append('../GeometricCoverSongs')
sys.path.append('../GeometricCoverSongs/SequenceAlignment')
from CSMSSMTools import *
from SyntheticCurves import *
from Alignments import *
from DTWGPU import *

def getPrecisionRecall(D, NPerClass = 10):
    PR = np.zeros(NPerClass-1)
    N = D.shape[0]
    #TODO: Finish this, compute average precision recall graph
    #using all point clouds as queries
    for i in range(N-1):
        currRow = D[i, :] #look at the ith row
        ans = np.argsort(currRow) #sort the row
        numerator = 0
        denominator = 0

        for x in np.nditer(ans): #look at each element in the row
            if (i != x): #bc don't want to exclude shape itself from comparison
                denominator += 1 #keeps record of the position we are in
            if (i != x) and (np.floor(x/10) == np.floor(i/10)):
                numerator += 1 #adds to precision
                if (numerator - 1 == 9):
                    continue;
                PR[numerator-1] += float(numerator) / denominator
    PR = PR/float(N)
    return PR

def doExperiment(N = 200, NPerClass = 40, K = 3, NBins = 50):
    WarpDict = getWarpDictionary(N)
    Curves = {}
    Curves['VivianiFigure8'] = lambda t: getVivianiFigure8(0.5, t)
    Curves['TSCubic'] = lambda t: getTschirnhausenCubic(1, t)
    Curves['TorusKnot23'] = lambda t: getTorusKnot(2, 3, t)
    Curves['TorusKnot35'] = lambda t: getTorusKnot(3, 5, t)
    Curves['PinchedCircle'] = lambda t: getPinchedCircle(t)
    Curves['Lissajous32'] = lambda t: getLissajousCurve(1, 1, 3, 2, 0, t)
    Curves['Lissajous54'] = lambda t: getLissajousCurve(1, 1, 5, 4, 0, t)
    Curves['ConeHelix'] = lambda t: getConeHelix(1, 16, t)
    Curves['Epicycloid1_3'] = lambda t: getEpicycloid(1.5, 0.5, t)
    #Curves['Epicycloid1_4'] = lambda t: getEpicycloid(2, 0.5, t)
    Xs = []
    for name in Curves:
        curve = Curves[name]
        for k in range(NPerClass):
            t = getWarpingPath(WarpDict, K, False)
            Xs.append(curve(t))

    NCurves = len(Xs)
    DDTW = np.zeros((NCurves, NCurves))
    DSSM = np.zeros((NCurves, NCurves))
    DD2 = np.zeros((NCurves, NCurves))
    for i in range(NCurves):
        x = Xs[i]
        SSMX = np.array(getCSM(x, x), dtype=np.float32)
        hx = 1.0*np.histogram(SSMX, bins=NBins, range=(0, 4))[0]
        hx = hx/np.sum(hx)
        gSSMX = gpuarray.to_gpu(np.array(SSMX, dtype = np.float32))
        print "Finished %i of %i..."%(i, NCurves)
        for j in range(i+1, NCurves):
            y = Xs[j]
            SSMY = np.array(getCSM(y, y), dtype=np.float32)
            hy = 1.0*np.histogram(SSMY, bins=NBins, range=(0, 4))[0]
            hy = hy/np.sum(hy)
            gSSMY = gpuarray.to_gpu(np.array(SSMY, dtype = np.float32))
            resGPU = doIBDTWGPU(gSSMX, gSSMY, False, False)
            DDTW[i, j] = resGPU
            DSSM[i, j] = np.sqrt(np.sum((SSMX-SSMY)**2))
            DD2[i, j] = np.sum(np.abs(np.cumsum(hx) - np.cumsum(hy)))
        sio.savemat("DExperiment.mat", {"DDTW":DDTW+DDTW.T, "DSSM":DSSM+DSSM.T, "DD2":DD2+DD2.T})
    return Xs

if __name__ == '__main__':
    NPerClass = 6
    D = sio.loadmat("DExperiment.mat")
    DDTW = D['DDTW']
    DSSM = D['DSSM']
    DD2 = D['DD2']
    p1 = getPrecisionRecall(DDTW)
    p2 = getPrecisionRecall(DSSM)
    p3 = getPrecisionRecall(DD2)
    plt.plot(p1, 'r')
    plt.hold(True)
    plt.plot(p2, 'b')
    plt.plot(p3, 'k')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    
    plt.show()

if __name__ == '__main__2':
    initParallelAlgorithms()
    N = 200
    NPerClass = 6
    Xs = doExperiment(NPerClass = NPerClass)
    c = plt.get_cmap('spectral')
    C = c(np.array(np.round(np.linspace(0, 255, N*2)), dtype=np.int32))
    C = C[N/2:N*3/2, 0:3]
    plotbgcolor = (0.15, 0.15, 0.15)
    for i in range(len(Xs)):
        x = Xs[i]
        plt.clf()
        SSM = getCSM(x, x)
        plt.subplot(121)
        plt.scatter(x[:, 0], x[:, 1], 20, c=C, edgecolor='none')
        ax = plt.gca()
        ax.set_axis_bgcolor(plotbgcolor)
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        plt.subplot(122)
        plt.imshow(SSM, cmap = 'afmhot')
        plt.savefig("%i.png"%i, bbox_inches = 'tight')