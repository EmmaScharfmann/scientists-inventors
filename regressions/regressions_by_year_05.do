***************************************************************************************


######################## INVENTORS SIs  ########################

use /home/fs01/spec1142/Emma/GateKeepers/regressions/inventors_years_cites_novelty_backward_cites05.dta, replace

rename number_citations cites

gen novelty_opp = - novelty

gen collaborators = ln(co_authors_active + co_authors_career + co_authors_only)

keep if year < 2017
keep if is_US == 1

* cites 

ppmlhdfe cites active  collaborators , absorb(i.inventor_id_int age_count#year#i.cpc_class_int ) 
estimates store cites_patents2
summarize cites active collaborators if e(sample)

* novelty 

reghdfe novelty_opp active collaborators , absorb(i.inventor_id_int age_count#year#i.cpc_class_int ) 
estimates store novelty_patents2
summarize novelty_opp active collaborators if e(sample)

* self cites 

*reghdfe self_cites_prop active co_authors_active co_authors_career co_authors_only , absorb(i.inventor_id_int age_count#year#i.cpc_class_int ) 
*estimates store self_cites_patents2
*summarize self_cites_prop active co_authors_active co_authors_career co_authors_only if e(sample)


* age cites 
*reghdfe age_citation active co_authors_active co_authors_career co_authors_only , absorb(i.inventor_id_int age_count#year#i.cpc_class_int ) 
*estimates store age_cites_patents2
*summarize age_citation active co_authors_active co_authors_career co_authors_only if e(sample)

*************** robustness check with other cpc fixed effects ********************
*ppmlhdfe cites active co_authors_active co_authors_career co_authors_only , absorb(i.inventor_id_int age_count#year#A#B#C#G#H#Y) 
*estimates store cites_patents

*reghdfe novelty_opp active co_authors_active co_authors_career co_authors_only , absorb(i.inventor_id_int age_count#year#A#B#C#G#H#Y) 
*estimates store novelty_patents

*ppmlhdfe top_5_percent active co_authors_active co_authors_career co_authors_only , absorb(i.inventor_id_int age_count#year#A#B#C#G#H#Y) 
*estimates store top_cites
*summarize top_5_percent active co_authors_active co_authors_career co_authors_only if e(sample)
*************** robustness check with other cpc fixed effects ********************



######################## PAPERS ################v

* load data 

use /home/fs01/spec1142/Emma/GateKeepers/regressions/scientist_years_cites_novelty_backward_cites05.dta, replace

rename count_year age_count

summarize novelty
local novelty_papers_sd = - 100/r(sd)

gen novelty_opp = - novelty
*gen self_cites_prop = self_cites / count_backward_cites

gen collaborators = ln(co_authors_active + co_authors_career + co_authors_only)


keep if year < 2017
keep if is_US == 1

* cites 

ppmlhdfe cites active collaborators, absorb(i.author_id_int   age_count#year#i.concept1_int ) 
estimates store cites_papers2
summarize cites active collaborators if e(sample)

* novelty 

reghdfe novelty_opp active collaborators , absorb(i.author_id_int   age_count#year#i.concept1_int ) 
estimates store novelty_papers2
summarize novelty_opp active collaborators if e(sample)

* self cites 

*reghdfe self_cites_prop active co_authors_active co_authors_career co_authors_only , absorb(i.author_id_int   age_count#year#i.concept1_int ) 
*estimates store self_cites_papers2
*summarize self_cites_prop active co_authors_active co_authors_career co_authors_only if e(sample)

* age cites 
*reghdfe age_cites active co_authors_active co_authors_career co_authors_only , absorb(i.author_id_int   age_count#year#i.concept1_int ) 
*estimates store age_cites_papers2
*summarize age_cites active co_authors_active co_authors_career co_authors_only if e(sample)



*************** robustness check with other concepts fixed effects ********************
*ppmlhdfe cites active co_authors_active co_authors_career co_authors_only, absorb(i.author_id_int *age_count#year#Medicine#Biology#Chemistry#Computer_science#Materials_science#Physics ) 
*estimates store cites_papers

*reghdfe novelty_opp active co_authors_active co_authors_career co_authors_only, absorb(i.author_id_int *age_count#year#Medicine#Biology#Chemistry#Computer_science#Materials_science#Physics ) 
*estimates store novelty_papers

*ppmlhdfe top5percent active co_authors_active co_authors_career co_authors_only, absorb(i.author_id_int *age_count#year#Medicine#Biology#Chemistry#Computer_science#Materials_science#Physics ) 
*estimates store top_cites
*************** robustness check with other cpc fixed effects ********************



######################## SAVE TABLES  ########################


esttab cites_papers2 novelty_papers2  cites_patents2 novelty_patents2  using /home/fs01/spec1142/Emma/GateKeepers/regressions/level1_conf05_individual_level_totcoll.tex, mtitles("Sum papers cites" "Mean paper novelty"  "Sum patents cites" "Average patent novelty" ) keep(active collaborators) star(* 0.10 ** 0.05 *** 0.01) collabels(none) label stats(r2 N , fmt(%9.4f %9.0f %9.0fc) labels("R-squared" "Number of observations" )) plain b(%9.4f) se(%9.4f) noabbrev se nonumbers lines parentheses replace fragment










