#!/usr/bin/python
# -*- coding: utf-8 -*
import re
import traceback

import sys

__author__ = "gisly"


from lxml import etree
import os
import codecs


def create_parent_tier_from_annotation_concatenation(filename, new_filename,
                                                     parent_tier, tier_to_concatenate,
                                                     new_tier_name, end_delimiter = '.'):
    srcTree = etree.parse(filename)
    parent_tier_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                parent_tier + '"]')[0]
    tier_to_concatenate_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                tier_to_concatenate + '"]')[0]


    for alignable_annotation in srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                   parent_tier + '"]/ANNOTATION/'
                                              'ALIGNABLE_ANNOTATION'):
        new_tier_element_annotation = etree.SubElement(new_tier_element, 'ANNOTATION')
        new_tier_element_alignable_annotation = \
            etree.SubElement(new_tier_element_annotation, 'ALIGNABLE_ANNOTATION',
            ANNOTATION_ID = new_tier_name + "_" + alignable_annotation.attrib['ANNOTATION_ID'],
            TIME_SLOT_REF1 = alignable_annotation.attrib['TIME_SLOT_REF1'],
            TIME_SLOT_REF2 = alignable_annotation.attrib['TIME_SLOT_REF2'])
        new_tier_annotation_value = etree.SubElement(new_tier_element_alignable_annotation,
                                                     'ANNOTATION_VALUE')
        new_tier_annotation_value.text = \
            get_concatenation(tier_to_concatenate_element, alignable_annotation.attrib['ANNOTATION_ID']) + end_delimiter

    all_tiers = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER')
    for tier in all_tiers:
        if tier.attrib.get('PARENT_REF') == parent_tier:
            tier.attrib['PARENT_REF'] = new_tier_name
            for annotation in tier.xpath('ANNOTATION/REF_ANNOTATION'):
                annotation.attrib['ANNOTATION_REF'] = new_tier_name + "_" + annotation.attrib['ANNOTATION_REF']


    srcTree.write(new_filename)

def create_child_tier_from_annotation_concatenation(filename, new_filename,
                                                    parent_tier, tier_to_concatenate, new_tier_name):
    srcTree = etree.parse(filename)
    tier_to_concatenate_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                tier_to_concatenate + '"]')[0]
    new_tier_element = etree.SubElement(srcTree.getroot(), 'TIER', DEFAULT_LOCALE = 'ru',
                                       LINGUISTIC_TYPE_REF = tier_to_concatenate_element.attrib['LINGUISTIC_TYPE_REF'],
                                       TIER_ID = new_tier_name)

    for parent_annotation in srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                   parent_tier + '"]/ANNOTATION/'
                                              'REF_ANNOTATION'):
        new_tier_element_annotation = etree.SubElement(new_tier_element, 'ANNOTATION')
        new_tier_element_ref_annotation = \
            etree.SubElement(new_tier_element_annotation, 'REF_ANNOTATION',
            ANNOTATION_ID = new_tier_name + '_' + parent_annotation.attrib['ANNOTATION_ID'],
            ANNOTATION_REF = parent_annotation.attrib['ANNOTATION_ID'])
        new_tier_annotation_value = etree.SubElement(new_tier_element_ref_annotation,
                                                     'ANNOTATION_VALUE')
        new_tier_annotation_value.text = get_concatenation(tier_to_concatenate_element,
                                                           parent_annotation.attrib['ANNOTATION_ID'],
                                                           '')
    srcTree.write(new_filename)


def create_child_gloss_tier_from_annotation_concatenation(filename,
                                                          new_filename,
                                                          parent_tier,
                                                          tier_to_concatenate_parent,
                                                          tier_to_concatenate, new_tier_name):
    srcTree = etree.parse(filename)
    tier_to_concatenate_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                tier_to_concatenate + '"]')[0]
    tier_to_concatenate_parent_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                       tier_to_concatenate_parent + '"]')[0]
    new_tier_element = etree.SubElement(srcTree.getroot(), 'TIER', DEFAULT_LOCALE = 'ru',
                                       LINGUISTIC_TYPE_REF = tier_to_concatenate_element.attrib['LINGUISTIC_TYPE_REF'],
                                       TIER_ID = new_tier_name)

    for parent_annotation in srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                   parent_tier + '"]/ANNOTATION/'
                                              'REF_ANNOTATION'):
        new_tier_element_annotation = etree.SubElement(new_tier_element, 'ANNOTATION')
        new_tier_element_ref_annotation = \
            etree.SubElement(new_tier_element_annotation, 'REF_ANNOTATION',
            ANNOTATION_ID = new_tier_name + '_' + parent_annotation.attrib['ANNOTATION_ID'],
            ANNOTATION_REF = parent_annotation.attrib['ANNOTATION_ID'])
        new_tier_annotation_value = etree.SubElement(new_tier_element_ref_annotation,
                                                     'ANNOTATION_VALUE')
        new_tier_annotation_value.text = get_child_concatenation(tier_to_concatenate_parent_element,
                                                                 tier_to_concatenate_element,
                                                           parent_annotation.attrib['ANNOTATION_ID'],
                                                           '')
    srcTree.write(new_filename)

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
    glosses_tier_type = glosses_tier_element.attrib['LINGUISTIC_TYPE_REF']
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

    original_new_tier_element = etree.SubElement(srcTree.getroot(), 'LINGUISTIC_TYPE',
                                                CONSTRAINTS='Symbolic_Subdivision',
                                                GRAPHIC_REFERENCES='false',
                                                LINGUISTIC_TYPE_ID=original_tier_type + "Mod",
                                                TIME_ALIGNABLE='false')

    if main_tier_type == morphemes_tier_type:
        dependent_tier_type = 'part'
        dependent_tier_element = etree.SubElement(srcTree.getroot(), 'LINGUISTIC_TYPE', CONSTRAINTS='Symbolic_Subdivision',
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
        russian_new_tier_element = etree.SubElement(srcTree.getroot(), 'LINGUISTIC_TYPE',
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


def copy_main_tier_to_child(filename, new_filename, main_tier, tier_model, new_tier, new_tier_parent):
    srcTree = etree.parse(filename)
    main_tier_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                      main_tier + '"]')[0]
    tier_model_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                      tier_model + '"]')[0]

    new_tier_element = etree.SubElement(srcTree.getroot(), 'TIER', DEFAULT_LOCALE='ru',
                                        LINGUISTIC_TYPE_REF=tier_model_element.attrib['LINGUISTIC_TYPE_REF'],
                                        TIER_ID=new_tier,
                                        PARENT_REF=new_tier_parent)
    for alignable_annotation in main_tier_element.xpath('ANNOTATION/'
                                              'ALIGNABLE_ANNOTATION'):
        new_tier_element_annotation = etree.SubElement(new_tier_element, 'ANNOTATION')
        new_tier_element_ref_annotation = \
            etree.SubElement(new_tier_element_annotation, 'REF_ANNOTATION',
            ANNOTATION_REF = new_tier_parent + '_' + alignable_annotation.attrib['ANNOTATION_ID'],
            ANNOTATION_ID = new_tier + '_' + alignable_annotation.attrib['ANNOTATION_ID'])
        new_tier_annotation_value = etree.SubElement(new_tier_element_ref_annotation,
                                                     'ANNOTATION_VALUE')
        new_tier_annotation_value.text = \
            alignable_annotation.getchildren()[0].text

    srcTree.write(new_filename)

def get_child_concatenation(tier_to_concatenate_parent_element, tier_to_concatenate_element, annotation_id,
                            delimiter=' '):
    concatenated_values = ''
    for annotation in tier_to_concatenate_parent_element.xpath('ANNOTATION/REF_ANNOTATION'
                                                              '[@ANNOTATION_REF="' +
                                                                      annotation_id + '"]'):
        curAnnotationValue = annotation.xpath('ANNOTATION_VALUE/text()')[0]

        """concatenated_values += '' + get_concatenation(tier_to_concatenate_element, annotation.attrib['ANNOTATION_ID'],
                                                 '-')"""
        if curAnnotationValue.startswith('-'):
            delim = '-'
        elif curAnnotationValue.startswith('='):
            delim = '-'
        else:
            delim = ' '
        concatenated_values += delim + get_concatenation(tier_to_concatenate_element, annotation.attrib['ANNOTATION_ID'],
                                                         '')
    return re.sub('\-+', '-', concatenated_values.strip('-').strip())



def get_concatenation(tier_to_concatenate_element, annotation_id, delimiter=' '):
    concatenated_values = ''
    for annotation_value in tier_to_concatenate_element.xpath('ANNOTATION/REF_ANNOTATION'
                                              '[@ANNOTATION_REF="' +
                                                annotation_id + '"]/ANNOTATION_VALUE/text()'):
        concatenated_values += delimiter + annotation_value
    return concatenated_values.strip()

def prepare_file(filename, output_folder, language_tier_name):
    new_filename = os.path.join(output_folder, os.path.basename(filename))
    create_parent_tier_from_annotation_concatenation(filename, new_filename, language_tier_name, "fonWord", "sentFon")
    create_child_tier_from_annotation_concatenation(new_filename, new_filename,
                                                                   "fonWord", "fon", "fonConcat")
    create_child_gloss_tier_from_annotation_concatenation(new_filename,new_filename,
                                                                         "fonWord", "fon", "gl", "glConcat")
    copy_main_tier_to_child(new_filename, new_filename,
                                           language_tier_name, "rus", language_tier_name + "Cyr", "sentFon")
    return new_filename

def preprocess_folder(folder, output_folder, meta_folder, language_tier_name = "ev"):
    with codecs.open(os.path.join(meta_folder, 'meta.csv'), 'w', 'utf-8') as fout:
        fout.write('filename\r\n')
        for base_filename in os.listdir(folder):
            filename = os.path.join(folder, base_filename)
            if os.path.isfile(filename) and filename.lower().endswith('.eaf'):
                print('starting to process: %s' % filename)
                try:
                    new_filename = prepare_file(filename, output_folder, language_tier_name)
                    fout.write(os.path.splitext(os.path.basename(new_filename))[0] + '\n')
                    print('processed: %s'  % filename)
                except Exception as e:
                    print(e)
                    print('error occurred when processing: %s' % filename)






"""create_parent_tier_from_annotation_concatenation(,
                                          "ev", "fonWord", "evFon")

create_child_tier_from_annotation_concatenation("D://ForElan//ForSIL_CORPUS//"
                                          "evenki_corpus//eaf//2007_Chirinda_Eldogir_Valentina_FSk9_test.eaf_new.eaf",
                                          "fonWord", "fon", "fonConcat")

create_child_gloss_tier_from_annotation_concatenation("D://ForElan//ForSIL_CORPUS//"
                                          "evenki_corpus//eaf//2007_Chirinda_Eldogir_Valentina_FSk9_test.eaf_new.eaf_new.eaf",
                                          "fonWord", "fon", "gl", "glConcat")"""

"""preprocess_folder("D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/evenki//test//",
                  "D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/evenki/eaf",
                  "D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/evenki")"""

"""preprocess_folder("D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/ket//test//",
                  "D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/ket/eaf",
                  "D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/ket",
                  "ket")"""

"""create_child_gloss_tier_from_annotation_concatenation("D://ForElan//OldMethod//1998_Sovrechka_Saygotina_Vera_LR//"
                                                "1998_Sovrechka_Saygotina_Vera_LR_transliterated_new.eaf",
"D://ForElan//OldMethod//1998_Sovrechka_Saygotina_Vera_LR//"
                                                "1998_Sovrechka_Saygotina_Vera_LR_transliterated_new2.eaf",
                                          "fonConcat", "fon", "gl", "glConcat");"""


folder = "D://Mansi/Corpus/corpus/mansi/preprocessing/"
folder_out = "D://Mansi/Corpus/corpus/mansi/eaf/"

for filename in os.listdir(folder):
    if filename.endswith(".eaf"):
        print(filename)
        try:
            convert_plain_file(os.path.join(folder, filename),
                      os.path.join(folder_out, filename),
                     "fonWord", "Morphemes", "Glosses", "Morphemes")
        except Exception as e:
            print(filename + ":" + str(e))
            traceback.print_exc(file=sys.stdout)

"""
convert_plain_file("D://Mansi/Corpus/corpus/mansi/preprocessing/ASN_SP_050818_potyr.eaf",
                   "D://Mansi/Corpus/corpus/mansi/eaf/ASN_SP_050818_potyr.eaf",
                     "fonWord", "Morphemes", "Glosses", "Morphemes")"""

