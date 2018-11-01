* SSM2220 SPICE Macro-model               4/90, Rev. A
*                                          DFB / PMI
*
*
* Copyright 1990 by Analog Devices, Inc.
*
* Refer to "README.DOC" file for License Statement.  Use of this model
* indicates your acceptance with the terms and provisions in the License Statement.
*
* Node assignments
*                C1
*                | B1 
*                | | E1
*                | | | E2
*                | | | | B2
*                | | | | | C2
*                | | | | | |
.SUBCKT SSM2220  1 2 3 5 6 7
Q1   1  2  3   PMAT
Q2   7  6  5   PMAT
D1   2  3      DMAT1
D2   6  5      DMAT1
D3   3  4      DMAT1
D4   5  4      DMAT1
D5   1  4      DMAT2
D6   7  4      DMAT2
.MODEL    DMAT1  D(IS=7.2E-16 RS=20)
.MODEL    DMAT2  D(IS=1E-14 VJ=0.6 CJO=68P)
.MODEL    PMAT PNP(BF=160 IS=1.4E-13 VAF=60 BR=5 VAR=7 RB=16
+ RC=12 RE=0.35 CJE=57P VJE=0.7 MJE=0.4 TF=1.08E-9 
+ TR=3E-8 CJC=40P VJC=0.55 MJC=0.5 CJS=0 IKF=160M)
.ENDS
