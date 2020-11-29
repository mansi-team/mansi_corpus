#!/usr/bin/python
# -*- coding: utf-8 -*

__author__ = "gisly"
import re
import traceback
import sys
from lxml import etree
import os



FOLDER = "D://Mansi/Corpus/corpus/mansi/preprocessing/"
FOLDER_OUT = "D://Mansi/Corpus/corpus/mansi/eaf/"



def convert_plain_file(filename, new_filename, word_tier_name,
                       morphemes_tier_name, glosses_tier_name, parent_name,
                       russian_tier_name = 'Russian',
                       original_tier_name = 'Mansi'):
    srcTree = etree.parse(filename)


    main_tier_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                      parent_name + '"]')[0]
    morphemes_tier_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                        morphemes_tier_name + '"]')[0]
    glosses_tier_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                         glosses_tier_name + '"]')[0]
    russian_tier_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                         russian_tier_name + '"]')[0]
    original_tier_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                           original_tier_name + '"]')[0]

    main_tier_type = main_tier_element.attrib['LINGUISTIC_TYPE_REF']
    morphemes_tier_type = morphemes_tier_element.attrib['LINGUISTIC_TYPE_REF']
    russian_tier_type = russian_tier_element.attrib['LINGUISTIC_TYPE_REF']
    original_tier_type = original_tier_element.attrib['LINGUISTIC_TYPE_REF']

    #if the morpheme tier has the same type as the main tier, change to to a dependent tier
    dependent_tier_type = morphemes_tier_type
    morphemes_all_independent = []
    glosses_all_independent = []
    russian_all_independent = []
    original_all_independent = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                      original_tier_name + '"]/ANNOTATION/'
                                              'ALIGNABLE_ANNOTATION/ANNOTATION_VALUE/text()')

    etree.SubElement(srcTree.getroot(), 'LINGUISTIC_TYPE',
                                                CONSTRAINTS='Symbolic_Subdivision',
                                                GRAPHIC_REFERENCES='false',
                                                LINGUISTIC_TYPE_ID=original_tier_type + "Mod",
                                                TIME_ALIGNABLE='false')

    if main_tier_type == morphemes_tier_type:
        dependent_tier_type = 'part'
        etree.SubElement(srcTree.getroot(), 'LINGUISTIC_TYPE', CONSTRAINTS='Symbolic_Subdivision',
                                                  GRAPHIC_REFERENCES='false',
                                                  LINGUISTIC_TYPE_ID=dependent_tier_type,
                                                  TIME_ALIGNABLE='false')
        morphemes_all_independent = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                      morphemes_tier_name + '"]/ANNOTATION/'
                                              'ALIGNABLE_ANNOTATION/ANNOTATION_VALUE/text()')
        glosses_all_independent = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                  glosses_tier_name + '"]/ANNOTATION/'
                                                                        'ALIGNABLE_ANNOTATION/ANNOTATION_VALUE/text()')


    # if the Russian tier has the same type as the main tier, change to to a dependent tier
    russian_new_tier_type = russian_tier_type
    if russian_tier_type == main_tier_type:
        russian_new_tier_type = 'RussianMod'
        etree.SubElement(srcTree.getroot(), 'LINGUISTIC_TYPE',
                                                  CONSTRAINTS='Symbolic_Subdivision',
                                                  GRAPHIC_REFERENCES='false',
                                                  LINGUISTIC_TYPE_ID=russian_new_tier_type,
                                                  TIME_ALIGNABLE='false')

        russian_all_independent = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                      russian_tier_name + '"]/ANNOTATION/'
                                              'ALIGNABLE_ANNOTATION/ANNOTATION_VALUE/text()')
    new_word_tier_element = etree.SubElement(srcTree.getroot(), 'TIER', DEFAULT_LOCALE='ru',
                                        LINGUISTIC_TYPE_REF=dependent_tier_type,
                                        TIER_ID=word_tier_name,
                                        PARENT_REF=parent_name)
    new_russian_tier_element = etree.SubElement(srcTree.getroot(), 'TIER', DEFAULT_LOCALE='ru',
                                                LINGUISTIC_TYPE_REF=russian_new_tier_type,
                                                TIER_ID=russian_tier_name + "Mod",
                                                PARENT_REF=parent_name)
    new_morpheme_tier_element = etree.SubElement(srcTree.getroot(), 'TIER', DEFAULT_LOCALE='ru',
                                        LINGUISTIC_TYPE_REF=dependent_tier_type,
                                        TIER_ID=morphemes_tier_name + "Concat",
                                        PARENT_REF=word_tier_name)
    new_gl_tier_element = etree.SubElement(srcTree.getroot(), 'TIER', DEFAULT_LOCALE='ru',
                                                 LINGUISTIC_TYPE_REF=dependent_tier_type,
                                                 TIER_ID=glosses_tier_name + "Concat",
                                                 PARENT_REF=word_tier_name)

    new_original_tier_element = etree.SubElement(srcTree.getroot(), 'TIER', DEFAULT_LOCALE='ru',
                                           LINGUISTIC_TYPE_REF=original_tier_type + "Mod",
                                           TIER_ID=original_tier_name + "Mod",
                                           PARENT_REF=parent_name)

    if len(morphemes_all_independent) != len(glosses_all_independent):
        raise Exception('Different number of lines in morphemes and glosses: '
                        + str(len(morphemes_all_independent)) + ' : ' + str(len(glosses_all_independent)))

    for index, parent_annotation in enumerate(srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                      parent_name + '"]/ANNOTATION/'
                                              'ALIGNABLE_ANNOTATION')):
        annotation_id = parent_annotation.attrib['ANNOTATION_ID']
        morphemes_all = morphemes_tier_element.xpath('ANNOTATION/REF_ANNOTATION'
                                                              '[@ANNOTATION_REF="' +
                                                                      annotation_id + '"]/ANNOTATION_VALUE/text()')

        russian_current = None
        original_current = None
        if main_tier_type == russian_tier_type:
            russian_current = russian_all_independent[index].strip()
            original_current = original_all_independent[index].strip()
        if morphemes_all:
            morphemes = morphemes_all[0]
        else:
            morphemes = morphemes_all_independent[index]

        words = morphemes.strip().split(" ")
        glosses_all = glosses_tier_element.xpath('ANNOTATION/REF_ANNOTATION'
                                              '[@ANNOTATION_REF="' +
                                              annotation_id + '"]/ANNOTATION_VALUE/text()')
        if glosses_all:
            glosses = glosses_all[0]
        else:
            glosses = glosses_all_independent[index]
        glosses_parts = glosses.strip().split(" ")

        if len(glosses_parts) != len(words):
            print(filename, glosses, words)
            #TODO
            ## raise Exception("len(glosses) != len(words)")


        new_russian_element_annotation = \
            etree.SubElement(new_russian_tier_element, 'ANNOTATION',
                             ANNOTATION_ID="rus" + annotation_id,
                             ANNOTATION_REF=annotation_id)
        new_russian_element_ref_annotation = \
            etree.SubElement(new_russian_element_annotation, 'REF_ANNOTATION',
                             ANNOTATION_ID="rus" + annotation_id,
                             ANNOTATION_REF=annotation_id)
        new_russian_annotation_value = etree.SubElement(new_russian_element_ref_annotation,
                                                     'ANNOTATION_VALUE')
        new_russian_annotation_value.text = russian_current

        new_original_element_annotation = \
            etree.SubElement(new_original_tier_element, 'ANNOTATION',
                             ANNOTATION_ID="original" + annotation_id,
                             ANNOTATION_REF=annotation_id)
        new_original_element_ref_annotation = \
            etree.SubElement(new_original_element_annotation, 'REF_ANNOTATION',
                             ANNOTATION_ID="original" + annotation_id,
                             ANNOTATION_REF=annotation_id)
        new_original_annotation_value = etree.SubElement(new_original_element_ref_annotation,
                                                        'ANNOTATION_VALUE')
        new_original_annotation_value.text = original_current

        previous_annotation_id = None
        for word_index, word in enumerate(words):
            new_tier_element_annotation = etree.SubElement(new_word_tier_element, 'ANNOTATION')
            word_annotation_id = word_tier_name + '_' + parent_annotation.attrib['ANNOTATION_ID'] \
                                 + "_" + str(word_index)
            new_tier_element_ref_annotation = \
                etree.SubElement(new_tier_element_annotation, 'REF_ANNOTATION',
                                 ANNOTATION_ID=word_annotation_id,
                                 ANNOTATION_REF=parent_annotation.attrib['ANNOTATION_ID'])
            if previous_annotation_id:
                new_tier_element_ref_annotation.attrib['PREVIOUS_ANNOTATION'] = previous_annotation_id
            new_tier_annotation_value = etree.SubElement(new_tier_element_ref_annotation,
                                                         'ANNOTATION_VALUE')
            word_cleared = re.sub('[\-\.\=]', '', word)
            new_tier_annotation_value.text = word_cleared
            previous_annotation_id = word_annotation_id

            new_morpheme_element_annotation = etree.SubElement(new_morpheme_tier_element, 'ANNOTATION')
            morpheme_annotation_id = morphemes_tier_name + '_' + parent_annotation.attrib['ANNOTATION_ID'] \
                                 + "_" + str(word_index)
            new_morpheme_element_ref_annotation = \
                etree.SubElement(new_morpheme_element_annotation, 'REF_ANNOTATION',
                                 ANNOTATION_ID=morpheme_annotation_id,
                                 ANNOTATION_REF=word_annotation_id)

            new_morpheme_element_ref_annotation_value = etree.SubElement(new_morpheme_element_ref_annotation,
                                                         'ANNOTATION_VALUE')
            new_morpheme_element_ref_annotation_value.text = word

            new_gloss_element_annotation = etree.SubElement(new_gl_tier_element, 'ANNOTATION')
            gloss_annotation_id = glosses_tier_name + '_' + parent_annotation.attrib['ANNOTATION_ID'] \
                                     + "_" + str(word_index)
            new_gloss_element_ref_annotation = \
                etree.SubElement(new_gloss_element_annotation, 'REF_ANNOTATION',
                                 ANNOTATION_ID=gloss_annotation_id,
                                 ANNOTATION_REF=word_annotation_id)

            new_gloss_element_ref_annotation_value = etree.SubElement(new_gloss_element_ref_annotation,
                                                                         'ANNOTATION_VALUE')
            if word_index < len(glosses_parts):
                new_gloss_element_ref_annotation_value.text = glosses_parts[word_index]


    srcTree.write(new_filename, encoding='utf-8')



def concatenate_annotations():
    exceptions = dict()
    successful_files = []
    for filename in os.listdir(FOLDER):
        if filename.endswith(".eaf"):
            try:
                convert_plain_file(os.path.join(FOLDER, filename),
                          os.path.join(FOLDER_OUT, filename),
                         "fonWord", "Morphemes", "Glosses", "Morphemes")
                successful_files.append(filename)
            except Exception as e:
                exceptions[filename] = str(e)
    return successful_files, exceptions

def main():
    successful_files, exceptions = concatenate_annotations()
    print('=========Success===============')
    print(successful_files)
    print('=========Exceptions============')
    print(exceptions)


if __name__ == '__main__':
    main()