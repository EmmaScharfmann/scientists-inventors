***************************************************************************************


######################## PATENTS ########################

* load data
use /home/fs01/spec1142/Emma/GateKeepers/regressions/patents_cites_novelty_05.dta, replace

summarize cites
local cites_patents_sd = 100/r(sd)

summarize novelty
local novelty_patents_sd = 100/r(sd)

gen novelty_op = - novelty


rename active_gk number_active_gks
rename career_gk number_career_gks
rename only_inventor number_only_authors


* cites 

ppmlhdfe cites number_active_gks number_career_gks number_only_authors , absorb(i.year#i.cpc_class_int#i.assignee) 
estimates store cites_patents
summarize cites number_active_gks number_career_gks number_only_authors if e(sample)


* novelty 

reghdfe novelty_op number_active_gks number_career_gks number_only_authors , absorb(i.year#i.cpc_class_int#i.assignee) 
estimates store novelty_patents
summarize novelty_op number_active_gks number_career_gks number_only_authors if e(sample)


* breakthrough 

ppmlhdfe top_5_percent number_active_gks number_career_gks number_only_authors , absorb(i.year#i.cpc_class_int#i.assignee) 
estimates store top_5_percent_patents
summarize top_5_percent number_active_gks number_career_gks number_only_authors if e(sample)


*************** robustness check with other cpc fixed effects ********************
*ppmlhdfe cites number_active_gks number_career_gks number_only_authors , absorb(i.year#i.assignee A B C D E F G H Y) 
*estimates store cites_patents2
*summarize cites number_active_gks number_career_gks number_only_authors if e(sample)

*reghdfe novelty_op number_active_gks number_career_gks number_only_authors  , absorb(i.year#i.assignee A B C D E F G H Y) 
*estimates store novelty_patents2
*summarize novelty_op number_active_gks number_career_gks number_only_authors if e(sample)

*ppmlhdfe top_5_percent number_active_gks number_career_gks number_only_authors , absorb(i.year#i.assignee A B C D E F G H Y) 
*estimates store top_5_percent_patents2
*summarize top_5_percent number_active_gks number_career_gks number_only_authors if e(sample)
*************** robustness check with other cpc fixed effects ********************




######################## PAPERS ################v


* load data 

use /home/fs01/spec1142/Emma/GateKeepers/science_gks_cites_novelty05.dta, replace

rename backward_cites science_citations

gen novelty_op = - novelty


summarize cites
local cites_papers_sd = 100/r(sd)

summarize novelty
local novelty_papers_sd = 100/r(sd) 


* cites 
ppmlhdfe cites number_active_gks number_career_gks number_only_authors , absorb(i.pubyear#concept1_int#i.institution_int) 
estimates store cites_papers 
summarize cites number_active_gks number_career_gks number_only_authors if e(sample)


* novelty 

reghdfe novelty_op number_active_gks number_career_gks number_only_authors , absorb(i.pubyear#concept1_int#i.institution_int) 
estimates store novelty_papers
summarize novelty_op number_active_gks number_career_gks number_only_authors if e(sample)


* breakthrough

ppmlhdfe top_5_percent number_active_gks number_career_gks number_only_authors , absorb(i.pubyear#concept1_int#i.institution_int) 
estimates store top_5_percent_papers
summarize top_5_percent number_active_gks number_career_gks number_only_authors if e(sample)



*************** robustness check with other concepts fixed effects ********************
* FE year x level 0 fields x institution  
*ppmlhdfe cites number_active_gks number_career_gks number_only_authors  , absorb(i.pubyear#Medicine#Biology#Chemistry#Computer_science#Materials_science#Physics#i.institution_int) 
*estimates store cites_papers2
*summarize cites number_active_gks number_career_gks number_only_authors if e(sample)

*reghdfe novelty_op number_active_gks number_career_gks number_only_authors , absorb(i.pubyear#Medicine#Biology#Chemistry#Computer_science#Materials_science#Physics#i.institution_int) 
*estimates store novelty_paper2
*summarize novelty_op number_active_gks number_career_gks number_only_authors if e(sample)

*ppmlhdfe top_5_percent number_active_gks number_career_gks number_only_authors  , absorb(i.pubyear#Medicine#Biology#Chemistry#Computer_science#Materials_science#Physics#i.institution_int) 
*estimates top_5_percent top_5_percent2
*summarize top_5_percent number_active_gks number_career_gks number_only_authors if e(sample)
*************** robustness check with other cpc fixed effects ********************




######################## SAVE TABLES  ########################

esttab cites_papers novelty_papers top_5_percent_papers cites_patents novelty_patents top_5_percent_patents using /home/fs01/spec1142/Emma/GateKeepers/regressions/level1_conf05_5percent.tex, mtitles("Papers citations" "Papers novelty" "Top 5% papers citations" "Patents citations" "Patents novelty" "Top 5% patent citations") keep(number_active_gks number_career_gks number_only_authors ) star(* 0.10 ** 0.05 *** 0.01) collabels(none) label stats(r2 N , fmt(%9.4f %9.0f %9.0fc) labels("R-squared" "Number of observations" )) plain b(%9.4f) se(%9.4f) noabbrev se nonumbers lines parentheses replace fragment





######################## SAVE COEFFICIENTS AS PLOTS  ########################

*coefplot cites_papers, bylabel(cites papers) rescale(100)|| cites_patents, bylabel(cites patents) rescale(100 ) ||  novelty_papers, bylabel(novelty papers) rescale(`novelty_papers_sd' ) || novelty_patents, bylabel(novelty patents) rescale(`novelty_patents_sd' ) || , keep(number_active_gks number_career_gks number_only_authors) vertical yline(0)  byopts(row(2)) xlabel(, ang(v)) coeflabels(number_active_gks = "active SI" number_career_gks = "career SI" number_only_authors = "not SI") ytitle(Percentage of increase per individual)          

*graph export "/home/fs01/spec1142/Emma/coefplot_ticpi_05_nb_poison.pdf", replace

*coefplot cites_papers2, bylabel(cites papers) rescale(100)|| cites_patents2, bylabel(cites patents) rescale(100 ) ||  novelty_paper2, bylabel(novelty papers) *rescale(`novelty_papers_sd' ) || novelty_patents2, bylabel(novelty patents) rescale(`novelty_patents_sd' ) || , keep(number_active_gks number_career_gks *number_only_authors) vertical yline(0)  byopts(row(2)) xlabel(, ang(v)) coeflabels(number_active_gks = "active SI" number_career_gks = "career SI" *number_only_authors = "not SI") ytitle(Percentage of increase per individual)          

*graph export "/home/fs01/spec1142/Emma/coefplot_ticp2_05_nb_poisson.pdf", replace


