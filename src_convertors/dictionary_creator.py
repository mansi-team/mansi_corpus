#!/usr/bin/python
# -*- coding: utf-8 -*
import os
import xml.etree.ElementTree as ET

import re

__author__ = "gisly"

MORPHEME_TIER_NAME = 'Morphemes'
GLOSS_TIER_NAME = 'Glosses'


def generate_morpheme_dictionary_for_word(filename, word, word_gloss, morpheme_dictionary):
    word_parts = re.split('[-]', word.strip('='))
    gloss_parts = re.split('[-]', word_gloss.strip('='))
    for i, word_part in enumerate(word_parts):
        if i >= len(gloss_parts):
            print(filename, word_parts, gloss_parts)
            continue
        gloss_part = gloss_parts[i]
        if word_part == '':
            continue
        word_parts_split_parts = word_part.split('=')
        gloss_part_split_parts = gloss_part.split('=')
        if len(word_parts_split_parts) == len(gloss_part_split_parts) and len(word_parts_split_parts) > 1:
            for j, word_parts_split_part in enumerate(word_parts_split_parts):
                gloss_part_split_part = gloss_part_split_parts[j]
                add_word_gloss(filename, word_parts_split_part, gloss_part_split_part, morpheme_dictionary)
        else:
            add_word_gloss(filename, word_part, gloss_part, morpheme_dictionary)


def add_word_gloss(filename, word_part, gloss_part, morpheme_dictionary):
    if word_part in morpheme_dictionary:
        if gloss_part in morpheme_dictionary[word_part]:
            morpheme_dictionary[word_part][gloss_part].add(filename)
        else:
            morpheme_dictionary[word_part][gloss_part] = {filename}
    else:
        morpheme_dictionary[word_part] = {gloss_part: {filename}}


def generate_morpheme_dictionary_for_sentence(filename, morphemes_text, glosses_text, morpheme_dictionary):
    words = morphemes_text.strip().split(' ')
    word_glosses = glosses_text.strip().split(' ')
    for i, word in enumerate(words):
        if i >= len(word_glosses):
            print(filename, word, word_glosses)
            continue
        word_gloss = word_glosses[i]
        generate_morpheme_dictionary_for_word(filename, word, word_gloss, morpheme_dictionary)


def generate_morpheme_dictionary_for_file(full_filename, morpheme_dictionary):
    filename = os.path.basename(full_filename)
    srcTree = ET.parse(full_filename).getroot()
    morpheme_tier_element = srcTree.find('./TIER[@TIER_ID="' +
                                         MORPHEME_TIER_NAME + '"]')
    gloss_tier_element = srcTree.find('./TIER[@TIER_ID="' +
                                      GLOSS_TIER_NAME + '"]')
    morphemes = morpheme_tier_element.findall('./ANNOTATION/ALIGNABLE_ANNOTATION/ANNOTATION_VALUE')
    glosses = gloss_tier_element.findall('./ANNOTATION/ALIGNABLE_ANNOTATION/ANNOTATION_VALUE')
    for i, morpheme_annotation in enumerate(morphemes):
        if i >= len(glosses):
            print(filename, morphemes, glosses)
            continue
        gloss_annotation = glosses[i]
        morphemes_text = morpheme_annotation.text
        glosses_text = gloss_annotation.text
        generate_morpheme_dictionary_for_sentence(filename, morphemes_text, glosses_text, morpheme_dictionary)


def generate_morpheme_dictionary(folder):
    morpheme_dictionary = dict()
    for filename in os.listdir(folder):
        if filename.endswith('.eaf'):
            full_filename = os.path.join(folder, filename)
            generate_morpheme_dictionary_for_file(full_filename, morpheme_dictionary)
    return morpheme_dictionary


def print_dictionary(dictionary, filename_out):
    with open(filename_out, 'w', encoding='utf-16', newline='') as fout:
        fout.write('morpheme\tgloss\tfilename\r\n')
        morphemes_sorted = sorted(list(dictionary.keys()))
        for morpheme in morphemes_sorted:
            meanings = dictionary[morpheme]
            glosses_sorted = sorted(list(meanings.keys()))
            for gloss in glosses_sorted:
                filenames = meanings[gloss]
                fout.write(morpheme + '\t' + gloss + '\t' + ','.join(sorted(filenames)) + '\r\n')


def create_dictionary(folder):
    output_filename = folder + os.path.sep + 'morpheme_dictionary.csv'
    dictionary = generate_morpheme_dictionary(folder)
    print_dictionary(dictionary, output_filename)


def correct_morphemes_glosses_in_file(filename, morphemes_replace, glosses_replace):
    has_changes = False
    tree_parsed = ET.parse(filename)
    srcTree = tree_parsed.getroot()
    morpheme_tier_element = srcTree.find('./TIER[@TIER_ID="' +
                                         MORPHEME_TIER_NAME + '"]')
    gloss_tier_element = srcTree.find('./TIER[@TIER_ID="' +
                                      GLOSS_TIER_NAME + '"]')
    morphemes_words = morpheme_tier_element.findall('./ANNOTATION/ALIGNABLE_ANNOTATION/ANNOTATION_VALUE')
    glosses_words = gloss_tier_element.findall('./ANNOTATION/ALIGNABLE_ANNOTATION/ANNOTATION_VALUE')
    for i, morpheme_annotation in enumerate(morphemes_words):
        gloss_annotation = glosses_words[i]
        morphemes_corrected, glosses_corrected = \
            correct_morphemes_glosses_for_word(filename, morpheme_annotation.text.strip(), gloss_annotation.text.strip(),
                                               morphemes_replace, glosses_replace)
        if morpheme_annotation.text.strip() != morphemes_corrected:
            morpheme_annotation.text = morphemes_corrected
            has_changes = True
        if gloss_annotation.text.strip() != glosses_corrected:
            print('=====', gloss_annotation.text, glosses_corrected)

            gloss_annotation.text = glosses_corrected
            has_changes = True
    if has_changes:
        tree_parsed.write(filename, encoding='utf-8', xml_declaration=True)


def correct_morphemes_glosses_for_word(filename, morpheme_annotation, gloss_annotation, morphemes_replace, glosses_replace):
    morphemes = morpheme_annotation.split(' ')
    glosses = gloss_annotation.split(' ')

    morphemes_corrected = ''
    glosses_corrected = ''

    for i, morphemes_text in enumerate(morphemes):
        glosses_text = glosses[i]
        word_parts = re.split('[-]', morphemes_text.strip('='))
        gloss_parts = re.split('[-]', glosses_text.strip('='))
        word_corrected = ''
        gloss_corrected = ''

        if len(word_parts) != len(gloss_parts):
            print("!!!!!:" + filename + ":" + morphemes_text + ":" + glosses_text)
            return morpheme_annotation, gloss_annotation
        for i, word_part in enumerate(word_parts):
            morpheme_to_replace = None
            gloss_to_replace = None

            if i >= len(gloss_parts):
                print(filename, word_parts, gloss_parts)
                continue
            gloss_part = gloss_parts[i]
            if word_part == '':
                continue
            word_parts_split_parts = word_part.split('=')
            gloss_part_split_parts = gloss_part.split('=')
            word_part_corrected = ''
            gloss_part_corrected = ''
            if len(word_parts_split_parts) == len(gloss_part_split_parts) and len(word_parts_split_parts) > 1:
                for j, word_parts_split_part in enumerate(word_parts_split_parts):
                    morpheme_to_replace = None
                    gloss_to_replace = None

                    gloss_part_split_part = gloss_part_split_parts[j]
                    if morphemes_replace:
                        morpheme_to_replace = morphemes_replace.get((word_parts_split_part, gloss_part_split_part))
                    if glosses_replace:
                        gloss_to_replace = glosses_replace.get((word_parts_split_part, gloss_part_split_part))

                    if morpheme_to_replace:
                        word_part_corrected +=  morpheme_to_replace + '='
                    else:
                        word_part_corrected += word_parts_split_part + '='
                    if gloss_to_replace:
                        gloss_part_corrected +=  gloss_to_replace + '='
                    else:
                        gloss_part_corrected +=  gloss_part_split_part + '='



            else:
                if morphemes_replace:
                    morpheme_to_replace = morphemes_replace.get((word_part, gloss_part))
                if glosses_replace:
                    gloss_to_replace = glosses_replace.get((word_part, gloss_part))
                if morpheme_to_replace:
                    word_part_corrected += '-' + morpheme_to_replace
                else:
                    word_part_corrected += '-' + word_part
                if gloss_to_replace:
                    gloss_part_corrected += '-' + gloss_to_replace
                else:
                    gloss_part_corrected += '-' + gloss_part

            word_corrected += '-' + word_part_corrected
            gloss_corrected += '-' + gloss_part_corrected
            if word_corrected.endswith('='):
                word_corrected = word_corrected[:-1]
            if gloss_corrected.endswith('='):
                gloss_corrected = gloss_corrected[:-1]

        word_corrected = word_corrected.replace('--', '-').replace(' -', '-').strip().strip('-')
        gloss_corrected = gloss_corrected.replace('--', '-').replace(' -', '-').strip().strip('-')
        if word_corrected.startswith('='):
            word_corrected = word_corrected[1:]
        if gloss_corrected.startswith('='):
            gloss_corrected = gloss_corrected[1:]
        if morphemes_text.endswith('=') and not(word_corrected.endswith('=')):
            word_corrected += '='
        if glosses_text.endswith('=') and not(gloss_corrected.endswith('=')):
            gloss_corrected += '='
        if word_corrected != morphemes_text:
            print('morphemes', morphemes_text, '---->', word_corrected)
        if gloss_corrected != glosses_text:
            print('glosses', glosses_text, '---->', gloss_corrected)
        morphemes_corrected += ' ' + word_corrected
        glosses_corrected += ' ' + gloss_corrected
    return morphemes_corrected.strip(), glosses_corrected.strip()



def correct_morphemes_glosses(folder, dictionary_filename):
    morphemes_replace, glosses_replace = read_dictionary(dictionary_filename)
    for filename in os.listdir(folder):
        if filename in morphemes_replace or filename in glosses_replace:
            correct_morphemes_glosses_in_file(os.path.join(folder, filename), morphemes_replace.get(filename),
                                              glosses_replace.get(filename))



def read_dictionary(filename):
    morphemes_replace = dict()
    glosses_replace = dict()
    with open(filename, 'r', encoding='utf-8') as fin:
        for line in fin:
            line_parts = line.strip().split(',')
            morpheme = line_parts[0]
            morpheme_corrected = line_parts[1]
            gloss = line_parts[2]
            gloss_corrected = line_parts[3]
            filename = line_parts[4]
            if morpheme_corrected != '':
                if filename not in morphemes_replace:
                    morphemes_replace[filename] = dict()
                morphemes_replace[filename][(morpheme, gloss)] = morpheme_corrected

            if gloss_corrected != '':
                if filename not in glosses_replace:
                    glosses_replace[filename] = dict()
                glosses_replace[filename][(morpheme, gloss)] = gloss_corrected

    return morphemes_replace, glosses_replace

folder = "D://Mansi//Corpus//corpus//mansi//preprocessing"
#create_dictionary(folder)
correct_morphemes_glosses(folder, "dictionary_corrected.csv")
