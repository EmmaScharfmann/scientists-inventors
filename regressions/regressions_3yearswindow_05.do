***************************************************************************************


######################## PATENTS ########################

* load data
use /home/fs01/spec1142/Emma/GateKeepers/regressions/patents_cites_novelty_3yearswindow_05.dta, replace

gen novelty_op = - novelty


rename active_gk number_active_gks
rename career_gk number_career_gks
rename only_inventor number_only_authors


* cites 

ppmlhdfe cites number_active_gks number_career_gks number_only_authors , absorb(i.year#i.cpc_class_int#i.assignee_id) 
estimates store cites_patents
summarize cites number_active_gks number_career_gks number_only_authors if e(sample)


* novelty 

reghdfe novelty_op number_active_gks number_career_gks number_only_authors , absorb(i.year#i.cpc_class_int#i.assignee_id) 
estimates store novelty_patents
summarize novelty_op number_active_gks number_career_gks number_only_authors if e(sample)


* self cites 

reghdfe self_cites_prop number_active_gks number_career_gks number_only_authors , absorb(i.year#i.cpc_class_int#i.assignee_id) 
estimates store self_cites_patents
summarize self_cites_prop number_active_gks number_career_gks number_only_authors if e(sample)


* age cites 

reghdfe age_citation number_active_gks number_career_gks number_only_authors , absorb(i.year#i.cpc_class_int#i.assignee_id) 
estimates store age_cites_patents
summarize age_citation number_active_gks number_career_gks number_only_authors if e(sample)



######################## PAPERS ################v


* load data 

use /home/fs01/spec1142/Emma/GateKeepers/regressions/science_papers_cites_novelty_3yearswindow_05.dta, replace

rename backward_cites science_citations

gen novelty_op = - novelty


* cites 
ppmlhdfe cites number_active_gks number_career_gks number_only_authors , absorb(i.pubyear#concept1_int#i.institution_int) 
estimates store cites_papers 
summarize cites number_active_gks number_career_gks number_only_authors if e(sample)


* novelty 

reghdfe novelty_op number_active_gks number_career_gks number_only_authors , absorb(i.pubyear#concept1_int#i.institution_int) 
estimates store novelty_papers
summarize novelty_op number_active_gks number_career_gks number_only_authors if e(sample)


* self cites 

reghdfe self_cites_prop number_active_gks number_career_gks number_only_authors , absorb(i.pubyear#concept1_int#i.institution_int) 
estimates store self_cites_papers
summarize self_cites_prop number_active_gks number_career_gks number_only_authors if e(sample)


* age cites 

reghdfe mean_age_backward_cite number_active_gks number_career_gks number_only_authors , absorb(i.pubyear#concept1_int#i.institution_int) 
estimates store age_cites_papers
summarize mean_age_backward_cite number_active_gks number_career_gks number_only_authors if e(sample)





######################## SAVE TABLES  ########################

esttab cites_papers novelty_papers self_cites_papers age_cites_papers cites_patents novelty_patents self_cites_patents age_cites_patents using /home/fs01/spec1142/Emma/GateKeepers/regressions/regression_level1_conf05_4models_3yearswindow_indicator.tex, mtitles("Papers citations" "Papers novelty" "Papers proportion self cites" "Papers mean age cites" "Patents citations" "Patents novelty" "Patents proportion self cites" "Patents mean age cites") keep(number_active_gks number_career_gks number_only_authors ) star(* 0.10 ** 0.05 *** 0.01) collabels(none) label stats(r2 N , fmt(%9.4f %9.0f %9.0fc) labels("R-squared" "Number of observations" )) plain b(%9.4f) se(%9.4f) noabbrev se nonumbers lines parentheses replace fragment



