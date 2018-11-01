* SSM2212 SPICE Macro-model                 3/2012, Rev. A
*                                      
*
* Copyright 2010 by Analog Devices, Inc.
*
*
* Node assignments
*              C1
*              | B1 
*              | | E1
*              | | | E2
*              | | | | B2
*              | | | | | C2
*              | | | | | |
.SUBCKT SSM2212  1 2 3 5 6 7
Q1   1  2  3   NMAT
Q2   7  6  5   NMAT
D1   3  2      DMAT1
D2   5  6      DMAT1
D3   4  3      DMAT1
D4   4  5      DMAT1
D5   4  1      DMAT2
D6   4  7      DMAT2
.MODEL    DMAT1  D(IS=2E-16 RS=20)
.MODEL    DMAT2  D(IS=1E-14 VJ=0.6 CJO=40E-12)
.MODEL    NMAT NPN(BF=500 IS=6E-13 VAF=150 BR=0.5 VAR=7
+ RB=13 RC=10 RE=0.3 CJE=82E-12 VJE=0.7 MJE=0.4 TF=0.3E-9 
+ TR=5E-9 CJC=33E-12 VJC=0.55 MJC=0.5 CJS=0 IKF=0.300
+ PTF=25)
.ENDS