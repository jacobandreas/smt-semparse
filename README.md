# Semantic parsing as machine translation

Most work on semantic parsing, even in variable-free formulations, has focused
on developing task- and formalism-specific models, often with expensive
training and decoding procedures. Can we use standard machine translation tools
to perform the same task? 

Yes. 

For a description of the system (it's really not complicated), see:

- J Andreas, A Vlachos and S Clark. "Semantic Parsing as Machine
  Translation". In ACL-short 2013. 
  http://www.cs.berkeley.edu/~jda/papers/avc_smt_semparse.pdf

You should also check out Carolin Haas's cdec-based reimplementation at
https://github.com/carhaas/cdec-semparse. 

### Getting started

Edit `dependencies.yaml` to reflect the configuration of your system.
`smt_semparse` should be set to the location of the repository root, the
`moses`, `srilm`, etc. entries to the roots of the corresponding external
dependencies, and `srilm_arch` to your machine architecture.

### Reproducing the ACL13 paper

Edit settings.yaml to choose a language and translation model for the particular
experiment you want to run. Use the following additional settings:

    lang=en -> stem=true,  symm=srctotgt
    lang=de -> stem=true,  symm=tgttosrc
    lang=el -> stem=false, symm=tgttosrc
    lang=th -> stem=false, symm=tgttosrc

Note that due to random MERT initialization your exact accuracy and F1 values
may differ slightly from those in the paper.

### Experimental things

Additional settings also allow you to do the following:

- Rebuild the phrase table after running MERT to squeeze a few more translation
  rules out of the training data. (Should give a nearly-imperceptible
  improvement in accuracy.)

- Filter rules which correspond to multi-rooted forests from the phrase table.
  (Should decrease accuracy.)

- Do full-supervised training on only a fraction of the dataset, and use the
  remaining monolingual data to reweight rules. (Mostly garbage---this data set
  is already too small to permit experiments which require holding out even more
  data.)

### Not implemented

MRL-to-NL &agrave; la Lu &amp; Ng 2011.

### Using a new dataset

Update `extractor.py` to create appropriately-formatted files in the working
directory. See the existing GeoQuery extractor for an example.
