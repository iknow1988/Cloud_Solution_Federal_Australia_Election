// party mentions count
function(doc) {
	party_twitter = ["animaljusticeAU", "AustFirstParty", "theabfparty", "AustChrist", "AuConservatives", "AustDems", "Greens", "AustralianLabor", "VictorianLabor", "AusProgressive", "AusWorkersParty", "centre_alliance", "chpparty", "CDPAustralia", "CECAustralia", "CountryLibs", "TasDLP", "JusticePartyAu", "voteflux", "fraser_anning", "KAPteam", "LibDemAus", "LNPQLD", "LiberalAus", "LoveAusOrLeave", "The_Nationals", "OneNationAus", "reasonaustralia", "RiseUpAus", "SciencePartyAus", "sffAustralia", "SocialistAllnce", "SEP_Australia", "VoteSustainable", "greatausparty", "storertim", "UnitedAusParty", "vic_socialists", "WestAusParty"];
	if (doc.entities.user_mentions) {
		for (i in doc.entities.user_mentions) {
			name = doc.entities.user_mentions[i].screen_name;
			temp = 0;
			for (i in party_twitter){
				if(name == party_twitter[j]){
					temp = 1;
					break;
				}
			}
			if(temp){
				emit(name, 1);
			}
		}
    }
}

// leader mentions count

function(doc) {
	leader_twitter = ["BrucePoon", "LeithEriksonABF", "corybernardi", "elisa_resce", "RichardDiNatale", "billshortenmp", "Rob4Canberra", "Stirling_G", "Senator_Patrick", "MakeMayoMatter", "Socworker63", "frednile", "gary_mla", "HumanHeadline", "nathanspataro", "fraser_anning", "RealBobKatter", "DavidLeyonhjelm", "DebFrecklington", "ScottMorrisonMP", "Kimmaree13", "M_McCormackMP", "PaulineHansonOz", "FionaPattenMLC", "PastorNalliah", "Andrea__Leong", "parrasocialist", "jcogan_sep", "William_Bourke", "RodCulletonGAP", "storertim", "CliveFPalmer", "sueabolton", "CrJulieMatheson"];
	if (doc.entities.user_mentions) {
		for (i in doc.entities.user_mentions) {
			name = doc.entities.user_mentions[i].screen_name;
			temp = 0;
			for (i in leader_twitter){
				if(name == leader_twitter[j]){
					temp = 1;
					break;
				}
			}
			if(temp){
				emit(name, 1);
			}
		}
    }
}

//hashtags count
function(doc){
	if(doc.entities.hashtags){
		for (i in doc.entities.hashtags) {
			name = doc.entities.hashtags[i].text;
			name = name.toLowerCase();
			emit(name, 1);
		}
    }
}

// locations count
function(doc){
	if(doc.hasOwnProperty("coordinates") && doc.coordinates){
		emit("Coordinates", 1);
    }
	else if(doc.hasOwnProperty("geo") && doc.geo){
		emit("Geo", 1);
	}
	else if(doc.place){
		emit(doc.place.full_name, 1);
	}
	else if(doc.hasOwnProperty("user") && doc.user.location){
		emit(doc.user.location, 1);
	}
	else{
		emit("No location",1);
	}
}


// Reduce function
function(keys, values) {
	return sum(values);
}
