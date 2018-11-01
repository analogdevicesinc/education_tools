* CD4007 NMOS and PMOS transistor SPICE models

* Typical - Typical Condition

.model CD4007-NMOS NMOS 
+ Level=1    Gamma= 0   Xj=0
+ Tox=1200n  Phi=.6     Rs=0      Kp=111u  Vto=2.0    Lambda=0.01
+ Rd=0       Cbd=2.0p   Cbs=2.0p  Pb=.8    Cgso=0.1p
+ Cgdo=0.1p  Is=16.64p  N=1

*The default W and L is 30 and 10 um respectively and AD and AS
*should not be included.


.model CD4007-PMOS PMOS 
+ Level=1    Gamma= 0   Xj=0
+ Tox=1200n  Phi=.6     Rs=0      Kp=55u  Vto=-1.5   Lambda=0.04
+ Rd=0       Cbd=4.0p   Cbs=4.0p  Pb=.8   Cgso=0.2p
+ Cgdo=0.2p  Is=16.64p  N=1

*The default W and L is 60 and 10 um respectively and AD and AS
*should not be included.