* .MODEL 1N4735 D IS=15N N=2.22 BV=6.2 IBV=41M 
* +      RS=169M CJO=4P VJ=750M M=330M TT=100N

* 1N4735    6.2 Volt ñ5% 1W zener diode
.model 1N4735  D(Is=1.168f Rs=.9756 Ikf=0 N=1 Xti=3 Eg=1.11 Cjo=140p M=.3196
+               Vj=.75 Fc=.5 Isr=2.613n Nr=2 Bv=6.2 Ibv=4.9984 Nbv=.32088
+               Ibvl=184.78u Nbvl=.19558 Tbv1=443.55u)
*               Motorola        pid=1N4735      case=DO-41
*               89-9-19 gjg
*               Vz = 6.2 @ 41mA, Zz = 9 @ 1mA, Zz = 3.4 @ 5mA, Zz = 1.85 @ 20mA