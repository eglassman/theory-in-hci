# Theory in HCI

Theories are an abstract form of knowledge that is both summative and generative: they summarize evidence that has collectively been observed so far and predict observations that have not yet been collected. When translated into a particular concrete domain, they generate testable hypotheses. This translation and generation process can require researchers' deep reflection on both the theory and the domain of application. Generative Theories of Interaction [GToI] provides one methodology for this reflective process.

When their predictions are fulfilled, they provide explanations for observations, and when their predictions are violated, it's an opportunity to suggest refinements to the theory itself, e.g., the boundaries of its applicability. Theory can be collectively refined over unbounded time-scales by many independently operating researchers. Without engaging in theory, a field is at risk of generating thousands of papers that each produce units of knowledge, but do not result in much greater possible accumulated and even replicated higher-level knowledge, like the difference between a pile of a thousand bricks and a thousand bricks arranged to create a functional structure.

Theories are most potentially powerful when stated in the maximally general way to facilitate accurate predictions across the most diverse concrete situations possible. A theory contradicts concrete observations at its own peril, but it can be phrased to cover situations beyond than just the concrete observations that support it. In fact, constraining the stated theory by contradicting evidence---but not missing evidence---maximizes the generality of the current version of the theory, which may help researchers recognize its applicability in new situations, as long as the gap between this maximally general statement of the theory and data collected already is also characterized, so that researchers do not incorrectly assume that missing confirmative data exists already.

Theory in HCI is particularly challenging because it is a manifold field: anywhere at least one human and one computational element are interacting, HCI knowledge is relevant. This poses many problems: 

First, there are many different entire fields of research about humans alone and together---with their own concepts, theories, and frameworks---that have implications for HCI. It's currently difficult to keep up with the many concepts, theories, and frameworks currently used in HCI, let alone those that may be relevant from other fields but are not yet known in HCI. And HCI is not unique in this respect; researchers in these other fields probably also do not know every concept, theory, and framework in their own field. That said, survey papers---that help individual researchers see a bigger picture than their more narrow bands of deep sub-field expertise---are more widely accepted in other fields than HCI ["The systematic review-lution" CHI 2023].

Second, for a given theory, a researcher can: 
(1) misunderstand the theory, 
(2) derive incorrect or suboptimal actionable principles [GToI], 
(3) fail to correctly identify whether aspects of a given situation or intervention satisfy an actionable principle or not [GToI analysis of artifacts stage],
(4) make false positive and false negative errors when analyzing the applicability of an actionable principle in a given situation or intervention [GToI critique of artifacts stage], 
(5) construct a situation or intervention that fails to fully fulfill an actionable principle [GToI constructive stage], 
(6) design an evaluation of a constructed situation or intervention that is incapable of generating observations that confirm or contradict the theory's predictions, 
and/or
(7) fail to notice the observations that would confirm or contradict the theory's predictions. 

Note that a theory does not need to already have a name and an accumulation of papers collecting data that support and refine it. It can be the design argument [cite] behind a particular system, which offers an explanation for why this particular system works and implicitly predicts why other systems with the same characteristics should work. It can be the more abstracted summary of findings from a grounded theory analysis of qualitative interviews.

# Data format

## Theory/thesis/concept/actionable principle schema-less "database"

### (Named) theory format

Note that theories have names and iterated on abstract sentences that explain testable predictions or descriptions of phenonema from which researchers can derive testable hypotheses.

{
"uid":"",
"theory_name": " ",
"alternative_names": [" ", ...],
"theory_in_sentences": [" ", ...],
"early_key_papers": [uid, ...],
"key_summative_papers_or_books": [uid, ...],
"key_authors": [" ", ...],
"source_field": " "
}

{
"uid":"",
"concept_name": " ",
"alternative_names": [" ", ...],
"concept_definition": [" ", ...],
"early_key_papers": [uid, ...],
"key_summative_papers_or_books": [uid, ...],
"key_authors": [" ", ...],
"source_field": " "
}

{
"uid":"",
"actionable_principle_name": " ",
"alternative_names": [" ", ...],
"actionable_principle__description": [" ", ...],
"early_key_papers": [uid, ...],
"key_summative_papers_or_books": [uid, ...],
"key_authors": [" ", ...],
"source_field": " "
}

{
"uid":"",
"framework_name": " ",
"alternative_names": [" ", ...],
"framework_description": [" ", ...],
"early_key_papers": [uid, ...],
"key_summative_papers_or_books": [uid, ...],
"key_authors": [" ", ...],
"source_field": " "
}

{
"uid":"",
"meta_theory_name": " ",
"alternative_names": [" ", ...],
"meta_theory_description": [" ", ...],
"early_key_papers": [uid, ...],
"key_summative_papers_or_books": [uid, ...],
"key_authors": [" ", ...],
"source_field": " "
}

[ ] actionable principle to use as example would be faceted browsing

## Paper format

{
"uid":"",
"thesis_statements": [uid, ...],
"concepts_defined": [uid, ...],
"actionable_principles" : [{ }, ...],
"theories_mentioned": [uid, ...],
"concepts_mentioned": [uid, ...],
"actionable_principles_derived_from" : [uid, ...],
"results_analyzed_with_respect_to_or_in_light_of" : [uid, ...],
"bibtex": " ",
"field": " ",
}

### Emerging (unnamed) theory format

{
"uid":"",
"thesis_statement": "",
"supporting_papers_and_explanations": [{uid, explanation}, ...],
"supporting_frameworks_and_explanations": [{uid, explanation}, ...],
"concepts_on_which_it_depends": [uid, ...],
"meta_theories": [uid, ...]
}


# Goals

1. Infrastructure for annual census of theory in HCI at, say, CHI, to answer questions of "basic current curricular needs", areas of over and under-examination, disambiguate different concepts with similar or same names, disambiguate same concept with different names, etc.
2. Contribute to / accumulate evidence in favor of theory refinement and emerging new theory 

# Scraps:

from which HCI researchers can derive actionable principles to inform HCI work [e.g., using Generative Theories of Interactions methodology] and test hypotheses [e.g., by instantiating novel interfaces that follow those principles and evaluating their impact on humans].


# Todos:

[ ] translate Remarkable notes from during Kavli
[ ] translate theory in HCI slides from Freiburg
[ ] is theory a form of meta analysis?
