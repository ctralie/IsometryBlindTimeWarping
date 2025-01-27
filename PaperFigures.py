"""
Make some extra figures for the paper
"""
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from mpl_toolkits.mplot3d import Axes3D
from Alignment.SyntheticCurves import *
from Alignment.Alignments import *
from Alignment.AlignmentTools import *
#from Alignment.DTWGPU import *

def makeColorbar(dim1, dim2, k):
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    plt.subplot(dim1, dim2, k)
    ax = plt.gca()
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad = 0.05)
    plt.colorbar(cax = cax)

def ConceptFigure():
    plotbgcolor = (0.15, 0.15, 0.15)
    np.random.seed(2)
    M = 100
    N = 160
    WarpDict = getWarpDictionary(N)
    t1 = np.linspace(0, 1, M)
    t2 = getWarpingPath(WarpDict, 2, False)

    X = getTschirnhausenCubic(1, t1)
    Y = getTschirnhausenCubic(1, t2)
    Y = applyRandomRigidTransformation(Y)
    Y = Y + np.array([-2.5, -1.5])

    SSMX = getSSM(X)
    SSMY = getSSM(Y)

    CSWM = doIBDTW(SSMX, SSMY)

    (DAll, CSM, backpointers, path) = DTWCSM(CSWM)
    pathProj = projectPath(path, M, N, 1)
    i11 = 15
    i12 = pathProj[i11, 1]
    i21 = 74
    i22 = pathProj[i21, 1]
    color1 = np.array([1.0, 0.0, 0.3])
    color2 = np.array([0.0, 0.5, 1.0])

    plt.figure(figsize=(12, 8.3))
    plt.subplot(231)
    plt.scatter(X[:, 0], X[:, 1], 20, np.arange(M), cmap = 'Spectral', edgecolor = 'none')
    plt.scatter(Y[:, 0], Y[:, 1], 20, np.arange(N), cmap = 'Spectral', edgecolor = 'none')
    plt.scatter(X[i11, 0], X[i11, 1], 150, color = color1, edgecolor = 'none')
    plt.scatter(X[i21, 0], X[i21, 1], 150, color = color2, edgecolor = 'none')
    plt.scatter(Y[i12, 0], Y[i12, 1], 150, color = color1, edgecolor = 'none')
    plt.scatter(Y[i22, 0], Y[i22, 1], 150, color = color2, edgecolor = 'none')
    plt.axis('equal')
    plt.title("Time-Ordered Point Clouds")
    ax = plt.gca()
    ax.set_axis_bgcolor(plotbgcolor)

    plt.subplot(232)
    plt.imshow(SSMX, interpolation = 'nearest', cmap = 'gray')
    plt.plot(np.arange(M), i11*np.ones(M), color = color1, lineWidth=4)
    plt.plot(np.arange(M), i21*np.ones(M), color = color2, lineWidth=4)
    plt.scatter(-2*np.ones(M), np.arange(M), 50, np.arange(M), cmap = 'Spectral', edgecolor = 'none')
    plt.scatter(np.arange(M), -2*np.ones(M), 50, np.arange(M), cmap = 'Spectral', edgecolor = 'none')
    plt.xlim([-4, M])
    plt.ylim([M, -4])
    plt.title("SSM 1")
    plt.xlabel("Time Index")
    plt.ylabel("Time Index")

    plt.subplot(233)
    plt.imshow(SSMY, interpolation = 'nearest', cmap = 'gray')
    plt.plot(np.arange(N), i12*np.ones(N), color = color1, lineWidth=4, lineStyle='--')
    plt.plot(np.arange(N), i22*np.ones(N), color = color2, lineWidth=4, lineStyle='--')
    plt.scatter(-2*np.ones(N), np.arange(N), 50, np.arange(N), cmap = 'Spectral', edgecolor = 'none')
    plt.scatter(np.arange(N), -2*np.ones(N), 50, np.arange(N), cmap = 'Spectral', edgecolor = 'none')
    plt.xlim([-5, N])
    plt.ylim([N, -5])
    plt.title("SSM 2")
    plt.xlabel("Time Index")
    plt.ylabel("Time Index")

    plt.subplot(234)
    plt.imshow(np.log(CSWM), cmap = 'afmhot', interpolation = 'nearest')
    plt.scatter(path[:, 1], path[:, 0], 2, color='c')
    plt.xlim([0, CSWM.shape[1]])
    plt.ylim([CSWM.shape[0], 0])
    plt.xlabel("Time Index 2")
    plt.ylabel("Time Index 1")
    plt.title("Cross-Similarity Warp Matrix\n(CSWM)")

    plt.subplot(235)
    plt.plot(np.arange(M), SSMX[i11, :], color = color1)
    plt.plot(np.arange(N), SSMY[i12, :], color = color1, lineStyle='--')
    plt.ylim([0, np.max(SSMX)])
    ax = plt.gca()
    #ax.set_axis_bgcolor(plotbgcolor)
    plt.title("Correspondence 1")
    plt.xlabel("Time Index")
    plt.ylabel("Distance")
    plt.legend(["SSM 1 Row %i"%i11, "SSM 2 Row %i"%i12], fontsize=12, loc = (0.02, 0.8))

    plt.subplot(236)
    plt.plot(np.arange(M), SSMX[i21, :], color = color2)
    plt.plot(np.arange(N), SSMY[i22, :], color = color2, lineStyle='--')
    plt.ylim([0, np.max(SSMX)])
    ax = plt.gca()
    #ax.set_axis_bgcolor(plotbgcolor)
    plt.title("Correspondence 2")
    plt.xlabel("Time Index")
    plt.ylabel("Distance")
    plt.legend(["SSM 1 Row %i"%i21, "SSM 2 Row %i"%i22], fontsize=12, loc = (0.02, 0.8))

    plt.savefig("IntroFigure.svg", bbox_inches = 'tight')

def IBDTWExample(compareCPU = False):
    initParallelAlgorithms()

    np.random.seed(6)
    M = 200
    N = 200
    t1 = np.linspace(0, 1, M)
    WarpDict = getWarpDictionary(N)
    t2 = getWarpingPath(WarpDict, 2, False)
    X1 = getPinchedCircle(t1)
    X2 = getPinchedCircle(t2)
    X2 = applyRandomRigidTransformation(X2)

    Kappa = 0.1
    NRelMag = 3
    NBumps = 3
    np.random.seed(40)
    (X3, Bumps) = addRandomBumps(X2, Kappa, NRelMag, NBumps)
    X3 = applyRandomRigidTransformation(X3)

    R = np.array([[0, -1], [1, 0]])
    X2 = X2.dot(R)
    X2 = X2 + np.array([[-1, -1.5]])
    X3 = X3 + np.array([6, -3])

    SSM1 = getCSM(X1, X1)
    SSM2 = getCSM(X2, X2)
    SSM3 = getCSM(X3, X3)

    if compareCPU:
        tic = time.time()
        D = doIBDTW(SSM1, SSM2)
        print("Elapsed Time CPU: %g"%(time.time() - tic))
        D2 = doIBDTWGPU(SSM1, SSM2, True, True)
        sio.savemat("D.mat", {"D":D, "D2":D2})

        plt.subplot(131)
        plt.imshow(D, cmap = 'afmhot')
        plt.subplot(132)
        plt.imshow(D2, cmap = 'afmhot')
        plt.subplot(133)
        plt.imshow(D - D2, cmap = 'afmhot')
        plt.show()

    CSWM12 = doIBDTWGPU(SSM1, SSM2, True, True)
    (DAll, CSM12, backpointers, path12) = DTWCSM(CSWM12)
    pathProj12 = projectPath(path12, M, N)
    res12 = getProjectedPathParam(pathProj12)

    CSWM13 = doIBDTWGPU(SSM1, SSM3, True, True)
    (DAll, CSM13, backpointers, path13) = DTWCSM(CSWM13)
    pathProj13 = projectPath(path13, M, N)
    res13 = getProjectedPathParam(pathProj13)

    plt.figure(figsize=(12, 8))
    plt.subplot(231)
    plt.imshow(SSM1, cmap = 'afmhot', interpolation = 'nearest', aspect = 'auto')
    plt.axis('off')
    plt.title('SSM 1')
    plt.subplot(232)
    plt.imshow(SSM2, cmap = 'afmhot', interpolation = 'nearest', aspect = 'auto')
    plt.axis('off')
    plt.title('SSM 2')
    plt.subplot(233)
    plt.imshow(SSM3, cmap = 'afmhot', interpolation = 'nearest', aspect = 'auto')
    plt.axis('off')
    plt.title('SSM 3')

    plt.subplot(234)
    plt.scatter(X1[:, 0], X1[:, 1], 10, c=res12['C1'], edgecolor='none')
    plt.text(np.mean(X1, 0)[0]-1.7, np.mean(X1, 0)[1]-0.5, '1', color='w', fontsize=36)
    plt.scatter(X2[:, 0], X2[:, 1], 10, c=res12['C2'], edgecolor='none')
    plt.text(np.mean(X2, 0)[0]-0.4, np.mean(X2, 0)[1]-0.4, '2', color='w', fontsize=36)
    plt.scatter(X3[:, 0], X3[:, 1], 10, c=res13['C2'], edgecolor='none')
    plt.text(np.mean(X3, 0)[0]-0.6, np.mean(X3, 0)[1]-0.3, '3', color='w', fontsize=36)
    plt.axis('equal')
    plotbgcolor = (0.15, 0.15, 0.15)
    ax = plt.gca()
    ax.set_axis_bgcolor(plotbgcolor)
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    #plt.xlim([-3.5, 6])
    #plt.ylim([-2.5, 6.5])
    plt.axis('equal')
    plt.title("TOPCs")

    plt.subplot(235)
    plt.imshow(CSWM12, cmap = 'afmhot', interpolation = 'nearest', aspect = 'auto')
    plt.hold(True)
    plt.scatter(path12[:, 1], path12[:, 0], 5, 'c', edgecolor = 'none')
    plt.xlim([0, CSWM12.shape[1]])
    plt.ylim([CSWM12.shape[0], 0])
    plt.xlabel("TOPC 2")
    plt.ylabel("TOPC 1")
    ax = plt.gca()
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    plt.title("CSWM 1 to 2, Cost = %.3g"%CSM12[-1, -1])

    plt.subplot(236)
    plt.imshow(CSWM13, cmap = 'afmhot', interpolation = 'nearest', aspect = 'auto')
    plt.hold(True)
    plt.scatter(path13[:, 1], path13[:, 0], 5, 'c', edgecolor = 'none')
    plt.xlim([0, CSWM13.shape[1]])
    plt.ylim([CSWM13.shape[0], 0])
    plt.xlabel("TOPC 3")
    plt.ylabel("TOPC 1")
    ax = plt.gca()
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    plt.title("CSWM 1 to 3, Cost = %.3g"%CSM13[-1, -1])

    plt.savefig("IBDTWExample.svg", bbox_inches='tight')

def Figure8Reparam():
    plt.figure(figsize=(14, 3))
    initParallelAlgorithms()
    plotbgcolor = (0.15, 0.15, 0.15)
    N = 200
    t = np.linspace(0, 1, N)
    ut = t**2
    X1 = np.zeros((N, 2))
    X1[:, 0] = np.cos(2*np.pi*t)
    X1[:, 1] = np.sin(4*np.pi*t)

    X2 = np.zeros((N, 2))
    X2[:, 0] = np.cos(2*np.pi*ut)
    X2[:, 1] = np.sin(4*np.pi*ut)
    X2 = X2 + np.array([1, -2.2])

    plt.subplot(141)
    plt.scatter(X1[:, 0], X1[:, 1], 20, np.arange(N), cmap='Spectral', edgecolor = 'none')
    plt.text(0.5, -0.2, '$t$', fontsize=30, color = 'w')
    plt.scatter(X2[:, 0], X2[:, 1], 20, np.arange(N), cmap='Spectral', edgecolor = 'none')
    plt.text(1.2, -2.3, '$u(t)$', fontsize=24, color = 'w')
    ax = plt.gca()
    ax.set_axis_bgcolor(plotbgcolor)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.axis('equal')
    plt.title("Figure 8 Point Clouds")

    plt.subplot(142)
    plt.plot(t, t, 'b', label='t')
    plt.hold(True)
    plt.plot(t, ut, 'r', label='u(t)')
    plt.xlabel("t")
    plt.ylabel("u(t)")
    plt.title("Parameterization Functions")
    plt.legend(bbox_to_anchor=(0.45, 0.9))

    D1 = getCSM(X1, X1)
    D2 = getCSM(X2, X2)
    CSWM = doIBDTWGPU(D1, D2, True, True)
    (DAll, CSM, backpointers, path) = DTWCSM(CSWM)
    pathProj = projectPath(path, N, N, direction = 1)
    idxs = np.arange(0, N, 20)

    plt.subplot(143)
    plt.imshow(D1, interpolation = 'nearest', cmap = 'afmhot')
    for idx in idxs:
        plt.plot([idx, idx], [0, N], 'k', lineWidth=2)
        plt.plot([0, N], [idx, idx], 'k', lineWidth=2)
    plt.scatter(-2*np.ones(N), np.arange(N), 50, np.arange(N), cmap = 'Spectral', edgecolor = 'none')
    plt.scatter(np.arange(N), -2*np.ones(N), 50, np.arange(N), cmap = 'Spectral', edgecolor = 'none')
    plt.xlim([-6, N])
    plt.ylim([N, -6])
    plt.axis('off')
    plt.title("SSM $\gamma_8(t)$")

    plt.subplot(144)
    plt.imshow(D2, interpolation = 'nearest', cmap = 'afmhot')
    for idxother in idxs:
        idx = pathProj[idxother, 1]
        plt.plot([idx, idx], [0, N], 'k', lineWidth=2)
        plt.plot([0, N], [idx, idx], 'k', lineWidth=2)
    plt.scatter(-2*np.ones(N), np.arange(N), 50, np.arange(N), cmap = 'Spectral', edgecolor = 'none')
    plt.scatter(np.arange(N), -2*np.ones(N), 50, np.arange(N), cmap = 'Spectral', edgecolor = 'none')
    plt.xlim([-6, N])
    plt.ylim([N, -6])
    plt.axis('off')
    plt.title("SSM $\gamma_8(u(t))$")

    plt.savefig("Figure8Reparam.svg", bbox_inches = 'tight')

def Figure8RankNormalization():
    plt.figure(figsize=(11.5, 10))
    initParallelAlgorithms()
    N = 200
    t = np.linspace(0, 1, N)
    ut = t**2
    X1 = np.zeros((N, 2))
    X1[:, 0] = np.cos(2*np.pi*t)
    X1[:, 1] = np.sin(4*np.pi*t)

    X2 = np.zeros((N, 2))
    X2[:, 0] = np.cos(2*np.pi*ut)
    X2[:, 1] = np.sin(4*np.pi*ut)

    D1 = getCSM(X1, X1)
    D2 = getCSM(X2, X2)
    D1Norm = get2DRankSSM(D1)
    D2Norm = get2DRankSSM(D2)

    CSWM = doIBDTWGPU(D1, D2, True, True)
    (DAll, CSM, backpointers, path) = DTWCSM(CSWM)

    CSWMNorm = doIBDTWGPU(D1Norm, D2Norm, True, True)
    (DAll, CSM, backpointers, pathNorm) = DTWCSM(CSWMNorm)

    plt.subplot(221)
    plt.imshow(D1, cmap = 'afmhot', interpolation = 'nearest')
    plt.title("Original SSM")
    makeColorbar(2, 2, 1)

    plt.subplot(222)
    plt.imshow(D1Norm, cmap = 'afmhot', interpolation = 'nearest')
    plt.title("Normalized SSM")
    makeColorbar(2, 2, 2)

    plt.subplot(223)
    plt.imshow(CSWM, cmap = 'afmhot', interpolation = 'nearest')
    plt.scatter(path[:, 1], path[:, 0], 5, 'c', edgecolor = 'none')
    plt.xlim([0, N])
    plt.ylim([N, 0])
    plt.title("CSWM Original")

    plt.subplot(224)
    plt.imshow(CSWMNorm, cmap = 'afmhot', interpolation = 'nearest')
    plt.scatter(pathNorm[:, 1], pathNorm[:, 0], 5, 'c', edgecolor = 'none')
    plt.xlim([0, N])
    plt.ylim([N, 0])
    plt.title("CSWM Norm")

    plt.savefig("2DRankNorm.svg", bbox_inches = 'tight')

def Figure8InterpNormalization(L = 100):
    plt.figure(figsize=(11.5, 10))
    initParallelAlgorithms()
    N = 200
    t = np.linspace(0, 1, N)
    ut = t**2
    X1 = np.zeros((N, 2))
    X1[:, 0] = np.cos(2*np.pi*t)
    X1[:, 1] = np.sin(4*np.pi*t)

    X2 = np.zeros((N, 2))
    X2[:, 0] = np.cos(2*np.pi*ut)
    X2[:, 1] = np.sin(4*np.pi*ut)

    D1 = getCSM(X1, X1)
    D2 = getCSM(X2, X2)
    (D1Norm, D2Norm) = matchSSMDist(D1, D2, L)

    CSWM = doIBDTWGPU(D1, D2, True, True)
    (DAll, CSM, backpointers, path) = DTWCSM(CSWM)

    CSWMNorm = doIBDTWGPU(D1Norm, D2Norm, True, True)
    (DAll, CSM, backpointers, pathNorm) = DTWCSM(CSWMNorm)

    plt.subplot(221)
    plt.imshow(D1, cmap = 'afmhot', interpolation = 'nearest')
    plt.title("Original SSM")
    makeColorbar(2, 2, 1)

    plt.subplot(222)
    plt.imshow(D1Norm, cmap = 'afmhot', interpolation = 'nearest')
    plt.title("Normalized SSM")
    makeColorbar(2, 2, 2)

    plt.subplot(223)
    plt.imshow(CSWM, cmap = 'afmhot', interpolation = 'nearest')
    plt.scatter(path[:, 1], path[:, 0], 5, 'c', edgecolor = 'none')
    plt.xlim([0, N])
    plt.ylim([N, 0])
    plt.title("CSWM Original")

    plt.subplot(224)
    plt.imshow(CSWMNorm, cmap = 'afmhot', interpolation = 'nearest')
    plt.scatter(pathNorm[:, 1], pathNorm[:, 0], 5, 'c', edgecolor = 'none')
    plt.xlim([0, N])
    plt.ylim([N, 0])
    plt.title("CSWM Norm")

    plt.savefig("2DInterpNorm%i.svg"%L, bbox_inches = 'tight')

def EulerianInterp(L = 100):
    A = 100
    B = 60
    T = 50
    NPeriods = 3
    phi = 0
    N = T*NPeriods

    #Which row from which to extract a 1D profile
    Row = 50
    NCols = T + T/2
    colors = [[0.0, 0.5, 0.0], [0.0, 0.5, 1.0], [0.7, 0.0, 0.7], [0.5, 0.5, 0.5]]
    ssmcmap = 'afmhot'

    X = np.zeros((N, A+B))
    Is = np.arange(X.shape[1])
    ts = np.linspace(0, N + np.pi/3, N)
    ts = ts[0:N]
    thetas = 2*np.pi/T*ts + phi
    fs = (A/2)*np.cos(thetas)
    for t in range(N):
        X[t, :] = np.abs(fs[t] - Is + A/2 + B/2) < B/2

    D1 = getSSM(fs[:, None])
    D2 = getSSM(X)

    (D2N, D1N) = matchSSMDist(D2, D1, L)
    (D1N2, D2N2) = matchSSMDist(D1, D2, L)

    plt.figure(figsize=(14, 6))
    plt.subplot(241)
    plt.plot(fs)
    plt.xlabel("Time")
    plt.ylabel("Position")
    plt.title("Lagrangian Coordinates")

    plt.subplot(242)
    plt.title("Lagrangian SSM Discretized")
    plt.scatter(np.arange(NCols), Row*np.ones(NCols), 20, colors[0], edgecolor = 'none')
    plt.imshow(D1N, cmap = ssmcmap, interpolation = 'nearest')
    plt.axis('off')
    makeColorbar(2, 4, 2)

    plt.subplot(243)
    plt.title("Lagrangian SSM To Eulerian")
    plt.scatter(np.arange(NCols), Row*np.ones(NCols), 20, colors[1], edgecolor = 'none')
    plt.imshow(D1N2, cmap = ssmcmap, interpolation = 'nearest')
    plt.axis('off')
    makeColorbar(2, 4, 3)


    plt.subplot(245)
    plt.imshow(1-X, cmap = 'gray', interpolation = 'nearest')
    plt.xlabel("Pixels")
    plt.ylabel("Time")
    plt.title("Eulerian Coordinates")
    
    plt.subplot(246)
    plt.scatter(np.arange(NCols), Row*np.ones(NCols), 20, colors[2], edgecolor = 'none')
    plt.imshow(D2N, cmap = ssmcmap, interpolation = 'nearest')
    plt.title("Eulerian SSM To Lagrangian")
    plt.xlabel("Time")
    ax = plt.gca()
    ax.set_yticks([])
    makeColorbar(2, 4, 6)
    plt.subplot(247)
    plt.scatter(np.arange(NCols), Row*np.ones(NCols), 20, colors[3], edgecolor = 'none')
    plt.imshow(D2N2, cmap = ssmcmap, interpolation = 'nearest')
    plt.title("Eulerian SSM Discretized")
    plt.xlabel("Time")
    ax = plt.gca()
    ax.set_yticks([])
    makeColorbar(2, 4, 7)

    plt.subplot(2, 4, 4)
    plt.plot(D1N[Row, 0:NCols], c=colors[0], lineWidth=4, linestyle='--')
    plt.plot(D2N[Row, 0:NCols], c = colors[2], lineWidth=2)
    plt.plot(D2N2[Row, 0:NCols], c=colors[3], lineWidth=4, linestyle=':')
    plt.ylim([-0.1, 1.1])
    #plt.ylabel("Row %i SSM Value"%Row)
    ax = plt.gca()
    ax.yaxis.tick_right()
    plt.title("Eulerian To Lagrangian")

    plt.subplot(2, 4, 8)
    plt.plot(D1N[Row, 0:NCols], c=colors[0], lineWidth=4, linestyle=':')
    plt.plot(D2N2[Row, 0:NCols], c=colors[3], lineWidth=4, linestyle='--')
    plt.plot(D1N2[Row, 0:NCols], c = colors[1], lineWidth=2)
    plt.ylim([-0.1, 1.1])
    plt.xlabel("Time")
    #plt.ylabel("Row %i SSM Value"%Row)
    ax = plt.gca()
    ax.yaxis.tick_right()
    plt.title("Lagrangian To Eulerian")

    plt.savefig("EulerianInterp.svg", bbox_inches = 'tight')

def SyntheticResults():
    Types = ['GTW', 'IMW', 'DTW', 'DDTW', 'CTW', 'IBDTW', 'IBDTWN']
    Curves = {}
    Curves['VivianiFigure8'] = lambda t: getVivianiFigure8(0.5, t)
    Curves['TSCubic'] = lambda t: getTschirnhausenCubic(1, t)
    Curves['TorusKnot23'] = lambda t: getTorusKnot(2, 3, t)
    Curves['TorusKnot35'] = lambda t: getTorusKnot(3, 5, t)
    Curves['PinchedCircle'] = lambda t: getPinchedCircle(t)
    Curves['Lissajous32'] = lambda t: getLissajousCurve(1, 1, 3, 2, 0, t)
    Curves['Lissajous54'] = lambda t: getLissajousCurve(1, 1, 5, 4, 0, t)
    Curves['ConeHelix'] = lambda t: getConeHelix(1, 16, t)
    Curves['Epicycloid'] = lambda t: getEpicycloid(1.5, 0.5, t)

    AllErrors = {}
    for t in Types:
        AllErrors[t] = np.array([])

    for curve in Curves:
        #X = sio.loadmat("Results/Synthetic/%sErrors.mat"%curve)
        X = sio.loadmat("Results/Synthetic_DTWInit_HistMatch/%sErrors.mat"%curve)
        for t in Types:
            AllErrors[t] = np.concatenate((AllErrors[t], X['P%s'%t].flatten()), 0)

    N = AllErrors['GTW'].size
    X = np.zeros((N, len(AllErrors)))
    for i in range(len(Types)):
        X[:, i] = AllErrors[Types[i]]
    
    fac = 0.5
    plt.figure(figsize=(fac*12, fac*4))
    k = 0
    t = np.linspace(0, 1, 256)
    c = plt.get_cmap('Spectral')
    C = c(np.arange(256))
    for curve in Curves:
        Y = Curves[curve](t)
        i = int(k%3)
        j = int(k/3)
        if Y.shape[1] == 3:
            ax = plt.subplot2grid((3, 7), (i, j), projection = '3d')
            ax.scatter(Y[:, 0], Y[:, 1], Y[:, 2], c = C)
        else:
            plt.subplot2grid((3, 7), (i, j))
            plt.scatter(Y[:, 0], Y[:, 1], 20, c = C)
        plt.axis('equal')
        plt.axis('off')
        plt.title(curve)
        k += 1
    plt.subplot2grid((3, 7), (0, 3), colspan = 4, rowspan = 3)
    plt.boxplot(X, labels = Types)
    plt.yscale('log')
    #plt.ylim([0, 50])
    plt.xlabel("Alignment Algorithm")
    plt.ylabel("Alignment Error")
    plt.title("Synthetic Curve Alignment Results")
    plt.savefig("SyntheticBoxPlotDTWInit.svg", bbox_inches = 'tight')

def WeizmannResults():
    Types = ['GTW', 'IMW', 'DTW', 'DDTW', 'CTW', 'IBDTW', 'IBDTWN']
    AllErrors = sio.loadmat("Results/WeizmannErrors100.mat")
    N = AllErrors['PGTW'].size
    X = np.zeros((N, len(Types)))
    for i in range(len(Types)):
        X[:, i] = AllErrors["P%s"%Types[i]].flatten()
    
    fac = 0.8
    plt.figure(figsize=(fac*4, fac*3))
    plt.boxplot(X, labels = Types)
    plt.ylim([0, 7])
    #plt.ylim([0.1, 10])
    #plt.yscale('log')
    plt.xlabel("Alignment Algorithm")
    plt.ylabel("Alignment Error")
    plt.title("Weizmann Mask To EDT Results")
    plt.savefig("WeizmannResults.svg", bbox_inches = 'tight')

def BUResults():
    Types = ['GTW', 'IMW', 'DTW', 'DDTW', 'CTW', 'IBDTW', 'IBDTWN']
    AllErrors = sio.loadmat("Results/BUErrors.mat")
    N = AllErrors['PGTW'].size
    X = np.zeros((N, len(Types)))
    for i in range(len(Types)):
        X[:, i] = AllErrors["P%s"%Types[i]].flatten()
    
    fac = 0.8
    plt.figure(figsize=(fac*4, fac*3))
    plt.boxplot(X, labels = Types)
    #plt.yscale('log')
    plt.xlabel("Alignment Algorithm")
    plt.ylabel("Alignment Error")
    plt.title("BU4D Face 2D Video To 3D Video")
    plt.savefig("BUResults.svg", bbox_inches = 'tight')

def ClosedLoopResults():
    X = sio.loadmat("Results/ClosedLoops.mat")['Scores'].flatten()
    
    plt.figure(figsize=(6, 1))
    #plt.boxplot(X)
    #plt.yscale('log')
    #plt.ylabel("Alignment Error")
    
    bins = np.logspace(np.min(np.log10(X)), np.max(np.log10(X)), 50)
    
    plt.hist(X, bins = bins)
    plt.xlim([0.1, 100])
    plt.gca().set_xscale("log")

    plt.title("Closed Loop Alignment Errors")
    plt.xlabel("Alignment Errors")
    plt.ylabel("Counts")
    plt.savefig("ClosedLoops.svg", bbox_inches = 'tight')

if __name__ == '__main__':
    #ConceptFigure()
    #IBDTWExample()
    #Figure8Reparam()
    #Figure8Normalization()
    #Figure8InterpNormalization(100)
    #EulerianInterp(100)
    SyntheticResults()
    WeizmannResults()
    BUResults()
    ClosedLoopResults()
