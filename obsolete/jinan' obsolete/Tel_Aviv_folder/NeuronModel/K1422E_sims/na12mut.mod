TITLE na3
: Na current 
: modified from Jeff Magee. M.Migliore may97
: added sh to account for higher threshold M.Migliore, Apr.2002

NEURON {
	SUFFIX na12mut
	USEION na READ ena WRITE ina
	USEION k READ ek WRITE ik
	RANGE  gbar, ar2, theg, ina,gna,gk,ik
	GLOBAL vhalfs,sh,tha,qa,Ra,Rb,thi1,thi2,qd,qg,mmin,hmin,q10,Rg,qq,Rd,tq,thinf,qinf,vhalfs,a0s,zetas,gms,smax,vvh,vvs
}

PARAMETER {
sh   = 8	(mV)
	gbar = 0.010   	(mho/cm2)	
			gna
gk			
	tha  =  -28.76	(mV)		: v 1/2 for act	
	qa   = 5.41	(mV)		: act slope (4.5)		
	Ra   = 0.3282 (/ms)		: open (v)		
	Rb   = 0.1 	(/ms)		: close (v)		

	thi1  = -37.651	(mV)		: v 1/2 for inact 	
	thi2  = -30 	(mV)		: v 1/2 for inact 	
	qd   = 0.5	(mV)	        : inact tau slope
	qg   = 1.5      (mV)
	mmin=0.02	
	hmin=0.01			
	q10=2
	Rg   = 0.000092 	(/ms)		: inact recov (v) prev 0.01 s A alpha
	Rd   = .02657 	(/ms)		: inact (v)	
	qq   = -65        (mV)    : prev 10 = v 1/2 alpha
	tq   = -55      (mV)    : keep same k alpha

	thinf  = -48.4785 	(mV)		: inact inf slope	
	qinf  = 7.69	(mV)		: inact inf slope 

        vhalfs=-20	(mV)		: slow inact. prev -60 s v 1/2 beta
        a0s=0.00011	(ms)		: a0s=b0s prev 0.0003
        zetas=12	(1)
        gms=0.2		(1)
        smax=10		(ms)
        vvh=-10		(mV) : prev -58 k beta
        vvs=2		(mV)
        ar2=1		(1)		: 1=no inact., 0=max inact.
	ena		(mV)
	ek (mV)	
	Ena = 55	(mV)            : must be explicitly def. in hoc
	celsius
	v 		(mV)
}


UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(pS) = (picosiemens)
	(um) = (micron)
} 

ASSIGNED {
	ina 		(mA/cm2)
	ik 		(mA/cm2)
	
	theg		(mho/cm2)
	minf 		
	hinf 		
	mtau (ms)	
	htau (ms) 	
	sinf (ms)	
	taus (ms)
}
 

STATE { m h s}

BREAKPOINT {
        SOLVE states METHOD cnexp
        theg = gbar*m*m*m*h*s
		gna = theg*0.5464
	gk = theg*0.4536

:   ina = g*(v - ena)*(1e-3)
    ina = gna*(v - ena)*(1e-4) 	: define  gbar as pS/um2 instead of mllimho/cm2
	ik = gk*(v-ek)*(1e-4)
    

:	ina = gna * (v - ena)
} 

INITIAL {
	trates(v,ar2,sh)
	m=minf  
	h=hinf
	s=sinf
}


FUNCTION alpv(v) {
         alpv = 1/(1+exp((v-vvh-sh)/vvs))
}
        
FUNCTION alps(v) {  
  alps = exp(1.e-3*zetas*(v-vhalfs-sh)*9.648e4/(8.315*(273.16+celsius)))
}

FUNCTION bets(v) {
  bets = exp(1.e-3*zetas*gms*(v-vhalfs-sh)*9.648e4/(8.315*(273.16+celsius)))
}

LOCAL mexp, hexp, sexp

DERIVATIVE states {   
        trates(v,ar2,sh)      
        m' = (minf-m)/mtau
        h' = (hinf-h)/htau
        s' = (sinf - s)/taus
}

PROCEDURE trates(vm,a2,sh2) {  
        LOCAL  a, b, c, qt
        qt=q10^((celsius-24)/10)
	a = trap0(vm,tha+sh2,Ra,qa)
	b = trap0(-vm,-tha-sh2,Rb,qa)
	mtau = 1/(a+b)/qt
        if (mtau<mmin) {
		mtau=mmin
		}
	minf = a/(a+b)

	a = trap0(vm,thi1,Rd,qd) : +sh2 raus
	b = trap0(-vm,-thi2,Rg,qg) : - sh2 raus
	htau =  1/(a+b)/qt
        if (htau<hmin) {
		htau=hmin
		}
	hinf = 1/(1+exp((vm-thinf)/qinf)): -sh2 raus
	c=alpv(vm)
        sinf = c+a2*(1-c)
        taus = bets(vm)/(a0s*(1+alps(vm)))
        if (taus<smax) {
		taus=smax
		}
}

FUNCTION trap0(v,th,a,q) {
	if (fabs(v-th) > 1e-6) {
	        trap0 = a * (v - th) / (1 - exp(-(v - th)/q))
	} else {
	        trap0 = a * q
 	}
}	