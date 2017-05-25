import argparse
import os

from gensim.models import Word2Vec

from shorttext.utils.classification_exceptions import Word2VecModelNotExistException, AlgorithmNotExistException
import shorttext.classifiers.embed.sumvec.SumEmbedVecClassification as sumwv
import shorttext.classifiers.embed.nnlib.VarNNEmbedVecClassification as auto
import shorttext.classifiers.embed.nnlib.VarNNEmbedVecClassification as cnn
import shorttext.data.data_retrieval as ret
import pickle