*
*Zetex ZVN2110A Spice Model v1.1 Last Revised 3/5/00
*
.SUBCKT ZVN2110A 3 4 5
*               D G S
M1 3 2 5 5 MN2110a
M2 3 2 5 5 MN2110b
RG 4 2 200
RL 3 5 1E9
C1 2 5 50E-12
C2 3 2 5E-12
D1 5 3 DN2110a
*
.MODEL MN2110a NMOS VTO=2 RS=.1 RD=1.8 IS=1E-15 KP=0.3
+CBD=60E-12 PB=1 LAMBDA=2.6E-3
.MODEL MN2110b NMOS VTO=0.9 RS=2 KP=0.1 PB=1 LAMBDA=2.6E-3
.MODEL DN2110a D IS=1E-12 RS=0.37
.ENDS ZVN2110A
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