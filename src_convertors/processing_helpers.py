#!/usr/bin/python
# -*- coding: utf-8 -*
import re

import sys

__author__ = "gisly"
import os
import xml.etree.ElementTree as ET
import pymorphy2

GLOSS_POS_FILENAME = '../corpus/glosses_pos.csv'
GLOSS_POS = dict()
POS_NOUN = 'N'
POS_PRONOUN = 'PRON'
POS_ADJECTIVE = 'A'
POS_ADVERB = 'ADV'
POS_UNKNOWN = 'UNKN'
POS_VERB = 'V'
POS_NUMBER = 'Q'
POS_PREP = 'PREP'
POS_CONJ = 'CONJ'
POS_PRCL = 'PTCL'
POS_INTJ = 'INTJ'
POS_ADD = 'ADD'

PYMORPHY_POS_CORRESPONDENCE = {'NOUN' : [POS_NOUN],
                               'ADJF' : [POS_ADJECTIVE],
                               'ADJS' : [POS_ADJECTIVE],
                               'COMP' : [POS_ADJECTIVE, POS_ADVERB],
                               'VERB' : [POS_VERB],
                               'INFN' : [POS_VERB],
                               'PRTF' : [POS_VERB],
                               'PRTS' : [POS_VERB],
                               'GRND' : [POS_VERB],
                               'NUMR' : [POS_NUMBER],
                               'ADVB' : [POS_ADVERB],
                               'NPRO' : [POS_PRONOUN],
                               'PRED' : [POS_ADVERB],
                               'PREP' : [POS_PREP],
                               'CONJ' : [POS_CONJ],
                               'PRCL' : [POS_PRCL],
                                'INTJ' : [POS_INTJ],
                               'LATN' : [POS_UNKNOWN],
                               'PNCT' : [POS_UNKNOWN],
                               'UNKN' : [POS_UNKNOWN]
                               }
morph = pymorphy2.MorphAnalyzer()

def get_gloss_list_from_file(filename, gloss_tier_name):
    tree = ET.parse(filename)
    root = tree.getroot()
    gloss_set = set()
    gloss_elements = root.findall('./TIER[@TIER_ID="' + gloss_tier_name +
                                  '"]/ANNOTATION/ALIGNABLE_ANNOTATION/ANNOTATION_VALUE')
    for gloss_element in gloss_elements:
        gloss_set = gloss_set.union(get_gloss_set_from_string(gloss_element.text))
    return gloss_set


def get_gloss_list_from_folder(folder, gloss_tier_name):
    glosses_by_file = dict()
    for filename in os.listdir(folder):
        if is_eaf(filename):
            full_filename = os.path.join(folder, filename)
            glosses_from_file = get_gloss_list_from_file(full_filename, gloss_tier_name)
            for gloss in glosses_from_file:
                if gloss in glosses_by_file:
                    glosses_by_file[gloss].append(filename)
                else:
                    glosses_by_file[gloss]= [filename]
    return glosses_by_file


def is_eaf(filename):
    return filename.lower().endswith('.eaf')

def get_gloss_set_from_string(gloss_list):
    gloss_set = set()
    glosses = gloss_list.split(' ')
    for gloss in glosses:
        gloss_set = gloss_set.union(set(re.split('[\-\=]', gloss)))
    return gloss_set

def add_pos_to_file(filename, filename_out, gloss_tier_name):
    tree = ET.parse(filename)
    root = tree.getroot()
    gloss_tier = root.findall('./TIER[@TIER_ID="' + gloss_tier_name +'"]')[0]
    pos_tier = ET.SubElement(root, 'TIER', DEFAULT_LOCALE='ru',
                                        LINGUISTIC_TYPE_REF=gloss_tier.attrib['LINGUISTIC_TYPE_REF'],
                                        TIER_ID='Pos')
    for annotation_element in gloss_tier.findall('./ANNOTATION/ALIGNABLE_ANNOTATION'):
        annotation_value_element = annotation_element.findall('./ANNOTATION_VALUE')[0]
        pos_list = get_pos_list(annotation_value_element.text)
        pos_tier_annotation = ET.SubElement(pos_tier, 'ANNOTATION')
        pos_tier_alignable_annotation = ET.SubElement(pos_tier, 'ALIGNABLE_ANNOTATION',
                                                      ANNOTATION_ID='pos_' + annotation_element.attrib['ANNOTATION_ID'],
                                                      TIME_SLOT_REF1=annotation_element.attrib[
                                                          'TIME_SLOT_REF1'],
                                                      TIME_SLOT_REF2=annotation_element.attrib[
                                                          'TIME_SLOT_REF2']
                                                      )
        pos_tier_alignable_annotation = ET.SubElement(pos_tier, 'ANNOTATION_VALUE')
        pos_tier_alignable_annotation.text = ' '.join(pos_list)
    tree.write(filename_out)


def initialize_gloss_post_list():
    global GLOSS_POS
    with open(GLOSS_POS_FILENAME, 'r', encoding='utf-8') as fin:
        for line in fin:
            line_parts = line.strip().split('\t')
            if len(line_parts) < 2:
                continue
            GLOSS_POS[line_parts[0]] = set(line_parts[1].split(','))
            

def add_pos_to_folder(folder, gloss_tier_name):
    initialize_gloss_post_list()
    folder_out = os.path.join(folder, 'pos')
    if not os.path.exists(folder_out):
        os.mkdir(folder_out)
    for filename in os.listdir(folder):
        filename_full = os.path.join(folder, filename)
        if is_eaf(filename_full):
            filename_out = os.path.join(folder_out, filename)
            add_pos_to_file(filename_full, filename_out, gloss_tier_name)

def get_pos_list(glosses):
    pos_list = []
    for word_gloss in re.split('\s', glosses):
        word_gloss = word_gloss.strip()
        if word_gloss != '':
            pos_list.append(get_pos_for_word_gloss(word_gloss))
    return pos_list


def is_pronoun(lemma_gloss):
    if lemma_gloss.startswith('NEG.PRON'):
        return True
    pos_by_lemma = GLOSS_POS.get(lemma_gloss)
    if not pos_by_lemma:
        return False
    return POS_PRONOUN in pos_by_lemma


def get_possible_poses_for_morpheme(morpheme_gloss):
    return GLOSS_POS.get(morpheme_gloss)


def get_pos_correspondence(pymorphy_pos):
    if pymorphy_pos is None:
        return []
    pos_list = PYMORPHY_POS_CORRESPONDENCE.get(pymorphy_pos)
    if not pos_list:
        raise Exception('No correspondence for POS: ' + pymorphy_pos)
    return set(pos_list)


def get_possible_poses_for_lemma(lemma_gloss):
    if lemma_gloss.startswith('NEG=кусать'):
        debug = 1
    if lemma_gloss.startswith('NEG.PRON'):
        return set(POS_PRONOUN)

    pos_tags = set()
    word_analyses =  morph.parse(lemma_gloss.lower())
    for word_analysis in word_analyses:
        pymorphy_pos = word_analysis.tag.POS
        if pymorphy_pos is None:
            pymorphy_pos = word_analysis.tag._POS
            if pymorphy_pos is None:
                raise Exception('NO POS: '  + lemma_gloss + str(word_analysis))
        pos_tags = pos_tags.union(get_pos_correspondence(pymorphy_pos))
    return pos_tags

def is_addition(lemma_gloss):
    return lemma_gloss == 'ADD'

def is_particle(lemma_gloss):
    return lemma_gloss.startswith('PTCL')


def get_pos_for_word_gloss(word_gloss):
    if word_gloss.startswith('NEG='):
        word_gloss = word_gloss[4:]
    if word_gloss.startswith('PTCL='):
        word_gloss = word_gloss[5:]
    morpheme_glosses = re.split('[\-=]', word_gloss)
    if not morpheme_glosses:
        raise Exception('Empty gloss list: ' + word_gloss)
    lemma_gloss = morpheme_glosses[0]
    if len(morpheme_glosses) == 1:
        if is_pronoun(lemma_gloss):
            return POS_PRONOUN
        if is_particle(lemma_gloss):
            return POS_PRCL
        if is_addition(lemma_gloss):
            return POS_ADD
        if '.' in lemma_gloss:
            morpheme_glosses = lemma_gloss.split('.')
            if len(morpheme_glosses) > 1:
                lemma_gloss = morpheme_glosses[0]
            else:
                poses_for_lemma = get_possible_poses_for_lemma(lemma_gloss)
                if len(poses_for_lemma) != 1:
                    return POS_UNKNOWN
                return list(poses_for_lemma)[0]
    possible_pos_set = set()
    is_first = True
    for morpheme_gloss in morpheme_glosses[1:]:
        morpheme_poses = get_possible_poses_for_morpheme(morpheme_gloss)
        if morpheme_poses:
            if is_first:
                possible_pos_set = morpheme_poses
                is_first = False
            else:
                possible_pos_set = possible_pos_set.intersection(morpheme_poses)
    if not possible_pos_set:
        possible_pos_set = get_possible_poses_for_lemma(lemma_gloss)
    #several variants guessed by the suffixes
    if len(possible_pos_set) > 1:
        #try to guess from lemma
        old_possible_pos_set = possible_pos_set
        poses_from_lemma = get_possible_poses_for_lemma(lemma_gloss)
        possible_pos_set = possible_pos_set.intersection(poses_from_lemma)
        #if there's no intersection, try to exclude less probable variants
        if not possible_pos_set:
            if len(old_possible_pos_set) == 2 and POS_NOUN in old_possible_pos_set \
                and POS_PRONOUN in old_possible_pos_set:
                return POS_NOUN
            if len(old_possible_pos_set) == 2 and POS_VERB in old_possible_pos_set \
                and POS_PRONOUN in old_possible_pos_set:
                return POS_VERB
            print('Contradictory gloss set: ' + word_gloss + ':' + str(old_possible_pos_set))
            return '/'.join(sorted(list(old_possible_pos_set)))
        if len(possible_pos_set) == 2 and POS_ADVERB in possible_pos_set and POS_PRCL in possible_pos_set:
            return POS_ADVERB
        if len(possible_pos_set) == 2 and POS_VERB in possible_pos_set \
                and POS_PRONOUN in possible_pos_set:
            return POS_VERB
        if len(possible_pos_set) == 2 and POS_NOUN in possible_pos_set \
                and POS_PRONOUN in possible_pos_set:
            return POS_NOUN

        if len(possible_pos_set) > 1:
            #print('Cannot guess: ' + word_gloss + ':' + str(possible_pos_set))
            return '/'.join(sorted(list(possible_pos_set)))
    return list(possible_pos_set)[0]


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: processing_helpers.py <folder>')
    else:
        add_pos_to_folder(sys.argv[1], "Glosses")
