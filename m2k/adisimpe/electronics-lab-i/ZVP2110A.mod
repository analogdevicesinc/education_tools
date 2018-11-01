*
*Zetex ZVP2110A Spice Model v1.0 Last Revised 23/7/04
*
.SUBCKT ZVP2110A 3 4 5
*                D G S
M1 13 20 5 5 Pmod1
RG 4 2 65
RIN 2 5 1E9
RL 3 5 1.2E8
RD 3 13 Rmod1 2.5
C1 2 5 140E-12
**C2 3 2 15E-12
D1 3 5 Dmod1
D2 3 17 Dmod2
Egs1 2 17 2 5 1
Egt1 2 20 5 21 1
Vgt1 5 22 1
Igt1 5 21 1
Rgt 21 22 Rmod2 1
.MODEL Pmod1 PMOS VTO=-2.8 RS=2 IS=1E-15 KP=0.17
+CBD=105E-12 PB=1 LAMBDA=6E-3
.MODEL Dmod1 D IS=5E-12 RS=1
.MODEL Dmod2 D CJO=60e-12 IS=1e-30 N=10
.MODEL Rmod1 RES (TC1=8e-3 TC2=4.2E-5)
.MODEL Rmod2 RES (TC1=-2e-3 TC2=3e-6)
.ENDS ZVP2110A
*
*$
*
*                (c)  2005 Zetex Semiconductors plc
*
*   The copyright in these models  and  the designs embodied belong
*   to Zetex Semiconductors plc (" Zetex ").  They  are  supplied
*   free of charge by Zetex for the purpose of research and design
*   and may be used or copied intact  (including this notice)  for
*   that purpose only.  All other rights are reserved. The models
*   are believed accurate but  no condition  or warranty  as to their
*   merchantability or fitness for purpose is given and no liability
*   in respect of any use is accepted by Zetex PLC, its distributors
*   or agents.
*
*   Zetex Semiconductors plc, Zetex Technology Park, Chadderton,
*   Oldham, United Kingdom, OL9 9LL