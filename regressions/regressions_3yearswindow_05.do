***************************************************************************************


######################## PATENTS ########################

* load data
use /home/fs01/spec1142/Emma/GateKeepers/regressions/patents_cites_novelty_3yearswindow_05.dta, replace

keep if year < 2017
keep if is_US == 1

gen novelty_op = - novelty


rename active_gk number_active_gks
rename career_gk number_career_gks
rename only_inventor number_only_authors

gen has_active_SI = 0 
replace has_active_SI = 1 if number_active_gks > 0

gen has_career_SI = 0 
replace has_career_SI = 1 if number_career_gks > 0

gen tot_inventors = ln(number_active_gks + number_career_gks + number_only_authors)



* cites 

ppmlhdfe cites has_active_SI has_career_SI tot_inventors , absorb(i.year#i.cpc_class_int#i.assignee_id) 
estimates store cites_patents
summarize cites has_active_SI has_career_SI tot_inventors  if e(sample)

*ppmlhdfe cites number_active_gks number_career_gks number_only_authors , absorb(i.year#i.cpc_class_int#i.assignee_id) 
*estimates store cites_patents
*summarize cites number_active_gks number_career_gks number_only_authors if e(sample)


* novelty 

reghdfe novelty_op has_active_SI has_career_SI tot_inventors  , absorb(i.year#i.cpc_class_int#i.assignee_id) 
estimates store novelty_patents
summarize novelty_op has_active_SI has_career_SI tot_inventors  if e(sample)




######################## PAPERS ################v


* load data 

use /home/fs01/spec1142/Emma/GateKeepers/regressions/science_papers_cites_novelty_3yearswindow_05.dta, replace

keep if pubyear < 2017

rename backward_cites science_citations

gen novelty_op = - novelty

gen has_active_SI = 0 
replace has_active_SI = 1 if number_active_gks > 0

gen has_career_SI = 0 
replace has_career_SI = 1 if number_career_gks > 0

gen tot_authors = ln(number_active_gks + number_career_gks + number_only_authors)


* cites 
ppmlhdfe cites has_active_SI has_career_SI tot_authors , absorb(i.pubyear#concept1_int#i.institution_int) 
estimates store cites_papers 
summarize cites has_active_SI has_career_SI tot_authors if e(sample)


* novelty 

reghdfe novelty_op has_active_SI has_career_SI tot_authors , absorb(i.pubyear#concept1_int#i.institution_int) 
estimates store novelty_papers
summarize novelty_op has_active_SI has_career_SI tot_authors if e(sample)





######################## SAVE TABLES  ########################

esttab cites_papers novelty_papers  cites_patents novelty_patents using /home/fs01/spec1142/Emma/GateKeepers/regressions/regression_level1_conf05_4models_3yearswindow_indicator.tex, mtitles("Papers citations" "Papers novelty"  "Patents citations" "Patents novelty" ) keep(has_active_SI has_career_SI tot_authors ) star(* 0.10 ** 0.05 *** 0.01) collabels(none) label stats(r2 N , fmt(%9.4f %9.0f %9.0fc) labels("R-squared" "Number of observations" )) plain b(%9.4f) se(%9.4f) noabbrev se nonumbers lines parentheses replace fragment


