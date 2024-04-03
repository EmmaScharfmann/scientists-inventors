***************************************************************************************


######################## INVENTORS SIs  ########################

use /home/fs01/spec1142/Emma/GateKeepers/regressions/inventors_years_cites_novelty_02.dta, replace

rename number_citations cites

gen novelty_opp = - novelty


* cites 

ppmlhdfe cites active  co_authors_active co_authors_career co_authors_only , absorb(i.inventor_id_int age_count#year#i.cpc_class_int ) 
estimates store cites_patents2
summarize cites active co_authors_active co_authors_career co_authors_only if e(sample)

* novelty 

reghdfe novelty_opp active co_authors_active co_authors_career co_authors_only , absorb(i.inventor_id_int age_count#year#i.cpc_class_int ) 
estimates store novelty_patents2
summarize novelty_opp active co_authors_active co_authors_career co_authors_only if e(sample)

* breakthrough 

ppmlhdfe top_5_percent active co_authors_active co_authors_career co_authors_only , absorb(i.inventor_id_int age_count#year#i.cpc_class_int ) 
estimates store top_patents_cites2
summarize top_5_percent active co_authors_active co_authors_career co_authors_only if e(sample)



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

use /home/fs01/spec1142/Emma/GateKeepers/regressions/scientist_years_cites_novelty_02.dta, replace

rename count_year age_count

summarize novelty
local novelty_papers_sd = - 100/r(sd)

gen novelty_opp = - novelty


* cites 

ppmlhdfe cites active co_authors_active co_authors_career co_authors_only, absorb(i.author_id_int   age_count#year#i.concept1_int ) 
estimates store cites_papers2
summarize cites active co_authors_active co_authors_career co_authors_only if e(sample)

* novelty 

reghdfe novelty_opp active co_authors_active co_authors_career co_authors_only , absorb(i.author_id_int   age_count#year#i.concept1_int ) 
estimates store novelty_papers2
summarize novelty_opp active co_authors_active co_authors_career co_authors_only if e(sample)

* breakthrough 

ppmlhdfe top5percent active co_authors_active co_authors_career co_authors_only, absorb(i.author_id_int   age_count#year#i.concept1_int ) 
estimates store top_papers_cites2
summarize top5percent active co_authors_active co_authors_career co_authors_only if e(sample)

*************** robustness check with other concepts fixed effects ********************
*ppmlhdfe cites active co_authors_active co_authors_career co_authors_only, absorb(i.author_id_int *age_count#year#Medicine#Biology#Chemistry#Computer_science#Materials_science#Physics ) 
*estimates store cites_papers

*reghdfe novelty_opp active co_authors_active co_authors_career co_authors_only, absorb(i.author_id_int *age_count#year#Medicine#Biology#Chemistry#Computer_science#Materials_science#Physics ) 
*estimates store novelty_papers

*ppmlhdfe top5percent active co_authors_active co_authors_career co_authors_only, absorb(i.author_id_int *age_count#year#Medicine#Biology#Chemistry#Computer_science#Materials_science#Physics ) 
*estimates store top_cites
*************** robustness check with other cpc fixed effects ********************



######################## SAVE TABLES  ########################


esttab cites_papers2 novelty_papers2 top_papers_cites2 cites_patents2 novelty_patents2 top_patents_cites2 using /home/fs01/spec1142/Emma/GateKeepers/regressions/level1_conf02_year_poisson.tex, mtitles("Sum papers cites" "Average paper novelty" "Sum top5% papers cites" "Sum patents cites" "Average patent novelty" "Sum top5% patents cites" ) keep(active co_authors_active co_authors_career co_authors_only) star(* 0.10 ** 0.05 *** 0.01) collabels(none) label stats(r2 N , fmt(%9.4f %9.0f %9.0fc) labels("R-squared" "Number of observations" )) plain b(%9.4f) se(%9.4f) noabbrev se nonumbers lines parentheses replace fragment










