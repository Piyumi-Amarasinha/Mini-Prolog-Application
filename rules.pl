
% Veterinary Triage Expert System


:- dynamic(species/1).
:- dynamic(symptom_severity/1).
:- dynamic(alertness/1).
:- dynamic(appetite/1).
:- dynamic(breathing_difficulty/1).
:- dynamic(temperature/1).
:- dynamic(vomiting/1).
:- dynamic(pain_level/1).
:- dynamic(hydration/1).


% Rules: (Knowledge Base)


%% triage(Level, Message)
%% Level = one of [emergency, urgent, non_urgent, advice, observation]
%% Clauses are ordered most-critical-first; the cut commits to the
%% first applicable rule, so this is the authoritative decision logic.

% 1) Highest priority: general severe emergencies
triage(emergency, "Immediate veterinary attention required: severe symptoms with critical signs") :-
    symptom_severity(severe),
    (alertness(unconscious); breathing_difficulty(yes)),
    !.

% 2) Hypothermia combined with reduced alertness is critical
triage(emergency, "Hypothermia with reduced alertness; immediate warming and vet care required") :-
    temperature(low),
    (alertness(unconscious); alertness(lethargic)),
    !.

% 3) Persistent vomiting with dehydration risks rapid deterioration
triage(emergency, "Persistent vomiting with dehydration signs; immediate vet care required") :-
    vomiting(persistent),
    hydration(dehydrated),
    !.

% 4) Species-specific emergencies
triage(emergency, "Rabbit - reduced appetite can indicate GI stasis; seek immediate vet care") :-
    species(rabbit),
    symptom_severity(mild),
    appetite(slightly_reduced),
    !.

triage(emergency, "Bird - breathing difficulty detected; immediate attention required") :-
    species(bird),
    breathing_difficulty(yes),
    !.

% 5) General urgent
triage(urgent, "Visit vet within a few hours") :-
    symptom_severity(moderate),
    (alertness(lethargic); appetite(refused); breathing_difficulty(mild)),
    !.

% 5a) Fever combined with moderate severity warrants prompt attention
triage(urgent, "Fever combined with moderate symptoms; visit vet within a few hours") :-
    temperature(fever),
    symptom_severity(moderate),
    !.

% 5b) Severe pain on its own is urgent
triage(urgent, "Signs of severe pain; visit vet within a few hours") :-
    pain_level(severe),
    !.

% 5c) Persistent vomiting alone (without dehydration) is still urgent
triage(urgent, "Persistent vomiting noted; visit vet within a few hours") :-
    vomiting(persistent),
    !.

% 5d) Standalone hypothermia (alertness still active) needs prompt care
triage(urgent, "Low body temperature noted; keep your pet warm and seek veterinary care soon") :-
    temperature(low),
    !.

% 5e) Species-specific urgent rules
triage(urgent, "Cat - slightly reduced appetite; visit vet within a few hours") :-
    species(cat),
    symptom_severity(mild),
    appetite(slightly_reduced),
    !.

triage(urgent, "Bird - mild breathing difficulty; visit vet soon") :-
    species(bird),
    symptom_severity(mild),
    breathing_difficulty(mild),
    !.

triage(urgent, "Rabbit - concerning signs; visit vet within a few hours") :-
    species(rabbit),
    symptom_severity(mild),
    (alertness(lethargic); appetite(refused); breathing_difficulty(mild)),
    !.

% 6) Non-urgent: clean bill across the board
triage(non_urgent, "Monitor at home and schedule a routine check-up") :-
    symptom_severity(mild),
    alertness(active),
    appetite(normal),
    breathing_difficulty(no),
    temperature(normal),
    vomiting(none),
    pain_level(none),
    hydration(normal),
    !.

% 6a) Mild pain alone warrants a non-urgent check
triage(non_urgent, "Mild pain noted; schedule a check-up soon") :-
    pain_level(mild),
    !.

% 7) Advice (minor, watch-and-wait signs)
triage(advice, "Fever noted; monitor temperature and consult a vet if it persists or worsens") :-
    temperature(fever),
    !.

triage(advice, "Occasional vomiting noted; monitor diet and behavior") :-
    vomiting(occasional),
    !.

triage(advice, "Dehydration signs noted; ensure water access and monitor closely") :-
    hydration(dehydrated),
    !.

triage(advice, "No critical signs detected, keep observing") :-
    species(dog),
    symptom_severity(mild),
    alertness(active),
    appetite(slightly_reduced),
    breathing_difficulty(no),
    !.

% 8) Fallback: observation required
triage(observation, "Your pet's symptoms don't fit a standard profile; proceed with caution and contact a vet if condition worsens") :-
    !.

% Backwards-compatible wrapper: triage(Message) returns a formatted string
level_label(emergency, "EMERGENCY").
level_label(urgent, "URGENT").
level_label(non_urgent, "NON-URGENT").
level_label(advice, "ADVICE").
level_label(observation, "OBSERVATION").

triage(Message) :-
    triage(Level, Msg),
    level_label(Level, Label),
    atomic_list_concat([Label, ": ", Msg], Message).


% Symptom-weighted severity index (informational only)
%
% NOTE: this score is NOT used to decide the triage Level - the rule
% cascade above is authoritative. The score is a supplementary
% 0-100 "how concerning are the numbers" indicator shown in the UI,
% so an expert rule can correctly flag an emergency (e.g. rabbit GI
% stasis) even when the additive score alone would look low.


% Weights for individual symptom values
weight_severity(mild, 10).
weight_severity(moderate, 25).
weight_severity(severe, 50).

weight_alertness(active, 0).
weight_alertness(lethargic, 20).
weight_alertness(unconscious, 40).

weight_appetite(normal, 0).
weight_appetite(slightly_reduced, 10).
weight_appetite(refused, 30).

weight_breathing(no, 0).
weight_breathing(mild, 20).
weight_breathing(yes, 50).

weight_temperature(normal, 0).
weight_temperature(fever, 20).
weight_temperature(low, 30).

weight_vomiting(none, 0).
weight_vomiting(occasional, 10).
weight_vomiting(persistent, 25).

weight_pain(none, 0).
weight_pain(mild, 15).
weight_pain(severe, 30).

weight_hydration(normal, 0).
weight_hydration(dehydrated, 25).

% Species multipliers
species_multiplier(dog, 1.0).
species_multiplier(cat, 1.2).
species_multiplier(bird, 1.4).
species_multiplier(rabbit, 1.5).
species_multiplier(other, 1.0).

% compute_severity(Score, Percent, Ws, Wa, Wap, Wb, Wt, Wv, Wpn, Wh, Mult)
compute_severity(Score, Percent, Ws, Wa, Wap, Wb, Wt, Wv, Wpn, Wh, Mult) :-
    % gather current facts (use sensible defaults if missing)
    (species(Spec) -> true ; Spec = other),
    (symptom_severity(Sev) -> true ; Sev = mild),
    (alertness(Alt) -> true ; Alt = active),
    (appetite(Ap) -> true ; Ap = normal),
    (breathing_difficulty(Bd) -> true ; Bd = no),
    (temperature(Temp) -> true ; Temp = normal),
    (vomiting(Vom) -> true ; Vom = none),
    (pain_level(Pain) -> true ; Pain = none),
    (hydration(Hyd) -> true ; Hyd = normal),

    % lookup weights
    weight_severity(Sev, Ws),
    weight_alertness(Alt, Wa),
    weight_appetite(Ap, Wap),
    weight_breathing(Bd, Wb),
    weight_temperature(Temp, Wt),
    weight_vomiting(Vom, Wv),
    weight_pain(Pain, Wpn),
    weight_hydration(Hyd, Wh),
    (species_multiplier(Spec, Mult) -> true ; Mult = 1.0),

    Sum is Ws + Wa + Wap + Wb + Wt + Wv + Wpn + Wh,
    ScoreFloat is Sum * Mult,
    Score is round(ScoreFloat),

    % normalize to 0..100 using theoretical max
    MaxSum is 50 + 40 + 30 + 50 + 30 + 25 + 30 + 25,
    MaxMult is 1.5,                 % highest species multiplier (rabbit)
    MaxScoreFloat is MaxSum * MaxMult,
    ( MaxScoreFloat =:= 0 -> PercentFloat = 0 ; PercentFloat is (ScoreFloat / MaxScoreFloat) * 100 ),
    Percent is round(PercentFloat).

% triage_score(Level, Message, Score, Percent, Ws, Wa, Wap, Wb, Wt, Wv, Wpn, Wh, Mult)
% Level/Message come from the rule cascade (triage/2); Score/Percent/weights
% are the informational severity breakdown computed independently.
triage_score(Level, Message, Score, Percent, Ws, Wa, Wap, Wb, Wt, Wv, Wpn, Wh, Mult) :-
    compute_severity(Score, Percent, Ws, Wa, Wap, Wb, Wt, Wv, Wpn, Wh, Mult),
    triage(Level, Message).


% Explanation: human-readable contributing factors behind the result


contributing_factor("Severe symptom severity reported") :- symptom_severity(severe).
contributing_factor("Moderate symptom severity reported") :- symptom_severity(moderate).
contributing_factor("Animal is unconscious") :- alertness(unconscious).
contributing_factor("Animal is lethargic") :- alertness(lethargic).
contributing_factor("Breathing difficulty present") :- breathing_difficulty(yes).
contributing_factor("Mild breathing difficulty present") :- breathing_difficulty(mild).
contributing_factor("Appetite refused") :- appetite(refused).
contributing_factor("Appetite slightly reduced") :- appetite(slightly_reduced).
contributing_factor("Fever detected") :- temperature(fever).
contributing_factor("Low body temperature (hypothermia risk)") :- temperature(low).
contributing_factor("Persistent vomiting") :- vomiting(persistent).
contributing_factor("Occasional vomiting") :- vomiting(occasional).
contributing_factor("Severe pain indicated") :- pain_level(severe).
contributing_factor("Mild pain indicated") :- pain_level(mild).
contributing_factor("Dehydration signs present") :- hydration(dehydrated).
contributing_factor("Rabbit - higher sensitivity to GI/appetite changes") :- species(rabbit).
contributing_factor("Bird - higher sensitivity to breathing issues") :- species(bird).

explanation(Factors) :-
    findall(F, contributing_factor(F), Fs),
    ( Fs == [] -> Factors = ["No significant risk factors identified"] ; Factors = Fs ).


% Ask user questions (interactive)


ask_question(Question, Choices, Answer) :-
    format("~n~w ~w~n> ", [Question, Choices]),
    read(Ans),
    (member(Ans, Choices) -> Answer = Ans ;
        writeln("Invalid input, try again."),
        ask_question(Question, Choices, Answer)).


% Start the expert system (interactive CLI mode)


start :-
    writeln("=========================================="),
    writeln("         VETERINARY TRIAGE ASSISTANT       "),
    writeln("=========================================="),
    retractall(species(_)),
    retractall(symptom_severity(_)),
    retractall(alertness(_)),
    retractall(appetite(_)),
    retractall(breathing_difficulty(_)),
    retractall(temperature(_)),
    retractall(vomiting(_)),
    retractall(pain_level(_)),
    retractall(hydration(_)),

    ask_question("What is the animal species?", [dog, cat, bird, rabbit, other], S),
    asserta(species(S)),

    ask_question("What is the overall symptom severity? (mild / moderate / severe)",
                 [mild, moderate, severe], Sev),
    asserta(symptom_severity(Sev)),

    ask_question("What is the animal's alertness level? (active / lethargic / unconscious)",
                 [active, lethargic, unconscious], A),
    asserta(alertness(A)),

    ask_question("How is the animal's appetite? (normal / slightly_reduced / refused)",
                 [normal, slightly_reduced, refused], Ap),
    asserta(appetite(Ap)),

    ask_question("Is there any breathing difficulty? (no / mild / yes)",
                 [no, mild, yes], B),
    asserta(breathing_difficulty(B)),

    ask_question("Any fever or low body temperature? (normal / fever / low)",
                 [normal, fever, low], Temp),
    asserta(temperature(Temp)),

    ask_question("Is the animal vomiting? (none / occasional / persistent)",
                 [none, occasional, persistent], Vom),
    asserta(vomiting(Vom)),

    ask_question("What is the animal's pain level? (none / mild / severe)",
                 [none, mild, severe], Pain),
    asserta(pain_level(Pain)),

    ask_question("Any signs of dehydration? (normal / dehydrated)",
                 [normal, dehydrated], Hyd),
    asserta(hydration(Hyd)),

    nl,
    writeln("Analyzing condition..."), nl,
    triage_score(Level, Msg, Score, Percent, _, _, _, _, _, _, _, _, _),
    level_label(Level, Label),
    format("Recommendation [~w]: ~w~n", [Label, Msg]),
    format("Severity score: ~w (~w%%)~n", [Score, Percent]),
    nl,
    explanation(Factors),
    writeln("Contributing factors:"),
    forall(member(F, Factors), format(" - ~w~n", [F])),
    nl,
    writeln("Triage completed. Follow the suggested advice."),
    nl.
