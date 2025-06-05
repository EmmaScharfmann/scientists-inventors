**** all PQRs - n-1 match  **** 

* load data
use /home/fs01/spec1142/Emma/GateKeepers/reviews/pqrs_n_1_matched_10years_edu_cites_novelty_app_v2.dta, replace

keep if year - app_year <= 5
keep if conf > 0.5


egen mean_nov = mean(novelty)
egen std_nov = sd(novelty)
gen std_novelty = (- novelty + mean_nov) / std_nov

ppmlhdfe nb_papers PQR , absorb(i.pair)
estimates store nb_papers_all
summarize  nb_papers if e(sample)


ppmlhdfe cites PQR , absorb(i.pair)
estimates store tot_cites_all
summarize  cites if e(sample)


reghdfe mean_cites PQR , absorb(i.pair)
estimates store mean_cites_all
summarize  mean_cites if e(sample)


reghdfe std_novelty PQR , absorb(i.pair)
estimates store novelty_all
summarize  std_novelty if e(sample)

esttab nb_papers_all tot_cites_all mean_cites_all novelty_all using /home/fs01/spec1142/Emma/GateKeepers/reviews/regression_matched_scientists_n_1_05.tex, mtitles("Nb papers" "Total cites" "Mean cites" "Novelty") star(* 0.10 ** 0.05 *** 0.01) collabels(none) label stats(r2 N , fmt(%9.4f %9.0f %9.0fc) labels("R-squared" "Number of observations" )) plain b(%9.4f) se(%9.4f) noabbrev se nonumbers lines parentheses replace fragment



**** all PQRs - exact match ****

* load data
use /home/fs01/spec1142/Emma/GateKeepers/reviews/pqrs_exact_matched_10years_edu_cites_novelty_app_v2.dta, replace

keep if year - app_year <= 5 
keep if conf > 0.5

egen mean_nov = mean(novelty)
egen std_nov = sd(novelty)
gen std_novelty = (- novelty + mean_nov) / std_nov

ppmlhdfe nb_papers PQR , absorb(i.pair)
estimates store nb_papers_all
summarize  nb_papers if e(sample)


ppmlhdfe cites PQR , absorb(i.pair)
estimates store tot_cites_all
summarize  cites if e(sample)


reghdfe mean_cites PQR , absorb(i.pair)
estimates store mean_cites_all
summarize  mean_cites if e(sample)


reghdfe std_novelty PQR , absorb(i.pair)
estimates store novelty_all
summarize  std_novelty if e(sample)

esttab nb_papers_all tot_cites_all mean_cites_all novelty_all using /home/fs01/spec1142/Emma/GateKeepers/reviews/regression_matched_scientists_extact_05.tex, mtitles("Nb papers" "Total cites" "Mean cites" "Novelty") star(* 0.10 ** 0.05 *** 0.01) collabels(none) label stats(r2 N , fmt(%9.4f %9.0f %9.0fc) labels("R-squared" "Number of observations" )) plain b(%9.4f) se(%9.4f) noabbrev se nonumbers lines parentheses replace fragment


