#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright 2013 MetaBrainz Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import unittest
import json
from geordi.mappings.wcd import wcd

class TestMappingsWcd(unittest.TestCase):

    def setUp(self):
        with open('./geordi/tests/data/wcd_a-hilliard-songbook_david-james_flac_lossless_29969287.json', 'r') as data:
            self.data = json.load(data)

    def test_link_types(self):
        linktypes = wcd().link_types()
        self.assertTrue('artist_id' in linktypes)
        self.assertTrue('file' in linktypes)

    def test_extract_linked(self):
        data = self.data
        linked = wcd().extract_linked(data['_source'])

        self.assertEqual(linked.keys(), ['artist_id', 'version', 'file'])
        self.assertEqual(len(linked['file']), 27)
        self.assertEqual(len(linked['artist_id']), 17)

        expected = {
            u'artist_id': [{u'type': u'composer', u'name': u'Anonymous', u'wcd_artist_id': 37022},
                           {u'type': u'composer', u'name': u'Arvo P\xe4rt', u'wcd_artist_id': 8541},
                           {u'type': u'composer', u'name': u'Barry Guy', u'wcd_artist_id': 63503},
                           {u'type': u'composer', u'name': u'Elizabeth Liddle', u'wcd_artist_id': 709077},
                           {u'type': u'composer', u'name': u'Ivan Moody', u'wcd_artist_id': 709075},
                           {u'type': u'composer', u'name': u'James MacMillan', u'wcd_artist_id': 178194},
                           {u'type': u'composer', u'name': u'Joanne Metcalf', u'wcd_artist_id': 709078},
                           {u'type': u'composer', u'name': u'John Casken', u'wcd_artist_id': 709079},
                           {u'type': u'composer', u'name': u'Michael Finnissy', u'wcd_artist_id': 589371},
                           {u'type': u'composer', u'name': u'Morton Feldman', u'wcd_artist_id': 3613},
                           {u'type': u'composer', u'name': u'Paul Robinson', u'wcd_artist_id': 83530},
                           {u'type': u'composer', u'name': u'Piers Hellawell', u'wcd_artist_id': 709076},
                           {u'type': u'composer', u'name': u'Veljo Tormis', u'wcd_artist_id': 351616},
                           {u'type': u'artist', u'name': u'David James', u'wcd_artist_id': 253741},
                           {u'type': u'artist', u'name': u'John Potter', u'wcd_artist_id': 226954},
                           {u'type': u'artist', u'name': u'Rogers Covey-Crump', u'wcd_artist_id': 465002},
                           {u'type': u'artist', u'name': u'The Hilliard Ensemble', u'wcd_artist_id': 6807}],
            u'version': 2,
            u'file': [{u'sha1': u'06d7aa0b670e634acef81cd3c3b9bb923b5333a5', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'True Beautie', u'number': u'09', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 1/09 - True Beautie.flac', u'length': 38860, u'acoustid': [u'b6ea8370-02b1-40e2-ac82-93a4d0598b5a']},
                      {u'sha1': u'da2dec3e0dab0ce9d3d02710243daf25852d32c9', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u"Kullervo's Message", u'number': u'16', u'filename': u"A Hilliard Songbook New Music for Voices FLAC/Disc 1/16 - Kullervo's Message.flac", u'length': 636900, u'acoustid': [u'f57b6d75-6ebf-4d99-8fab-8e9f40e031ae']},
                      {u'sha1': u'eda97a67ec979cefdd822dc463c4c7fc7f530330', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'True Beautie', u'number': u'13', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 1/13 - True Beautie.flac', u'length': 31730, u'acoustid': [u'5301ee1e-ca5e-4676-93d8-1b1702251df6']},
                      {u'sha1': u'8a7c1908f697adcc05fde9f8c46d17b3f5eff674', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Emerodde', u'number': u'10', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 1/10 - Emerodde.flac', u'length': 124760, u'acoustid': [u'b9d15dd0-8bfd-484c-a1d4-a392eb485ad2']},
                      {u'sha1': u'8421d5241807635c5c604bba3d45fba2429b1aea', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Un Coup De D\xe9s', u'number': u'01', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 1/01 - Un Coup De D\xe9s.flac', u'length': 754400, u'acoustid': [u'eb08229f-ef86-4e56-8d15-2c2cbbf8ded0']},
                      {u'sha1': u'82c9130f0fc62dd0024081398f017051d30629aa', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'On Black And White', u'number': u'08', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 1/08 - On Black And White.flac', u'length': 116640, u'acoustid': [u'46c18896-1233-40e0-8844-1eec9ebb3673']},
                      {u'sha1': u'd3c684d815ce0c625549d9869a511cd01e1e1141', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'By Falshood', u'number': u'14', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 1/14 - By Falshood.flac', u'length': 158930, u'acoustid': [u'fd534b50-906f-45d4-92ac-b2517b6d4c48']},
                      {u'sha1': u'3e6e37d0a89af3a4ced887c0304a552b90508bc6', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Endechas y Canciones - IV. Ojos de la mi se\xf1ora', u'number': u'06', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 1/06 - Endechas y Canciones - IV. Ojos de la mi se\xf1ora.flac', u'length': 120020, u'acoustid': [u'40a23b82-3485-452c-a8bb-caefe43e6d27']},
                      {u'sha1': u'd2fbcc5e697a87d9829366b1f30caaf831a74428', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'True Beautie', u'number': u'11', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 1/11 - True Beautie.flac', u'length': 44260, u'acoustid': [u'6439989b-7e22-4cc5-9931-abafeabeb285']},
                      {u'sha1': u'b212cc6e17325d8e7583150fa7661510150df12c', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'True Beautie', u'number': u'07', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 1/07 - True Beautie.flac', u'length': 33260, u'acoustid': [u'd1d23835-42ef-4e0a-821c-7b8bbce49adb']},
                      {u'sha1': u'616911487f108cb841bafc0c48b1f3a0524437f0', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Iasent', u'number': u'12', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 1/12 - Iasent.flac', u'length': 62840, u'acoustid': [u'ef5dcbfc-d1ff-452d-9fc8-ae8f3c921d35']},
                      {u'sha1': u'd4cac5ab575bf9cfe951e928c45f9ded78136995', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Only', u'number': u'02', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 1/02 - Only.flac', u'length': 105760, u'acoustid': [u'2ec4f202-7575-4a4e-9232-547662ddd014']},
                      {u'sha1': u'52e90cb950f56e991495b5ad8a6306254da203df', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Endechas y Canciones - II. Endechas a la muerte de Guill\xe9n Peraza', u'number': u'04', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 1/04 - Endechas y Canciones - II. Endechas a la muerte de Guill\xe9n Peraza.flac', u'length': 490560, u'acoustid': [u'2c08add3-8fc1-4f68-a238-ca93c31f17ed']},
                      {u'sha1': u'd575e0bf6928cc7eddb65ec0d3ca98d13033d4f9', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Endechas y Canciones - III. Pu\xe9s mi pena veis', u'number': u'05', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 1/05 - Endechas y Canciones - III. Pu\xe9s mi pena veis.flac', u'length': 124770, u'acoustid': [u'b8b0011e-39cf-4a78-9986-37e77ec4e3bc']},
                      {u'sha1': u'dc52b5dc3de6795ae16f434b714d2b2aa219a5b9', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Endechas y Canciones - I. no pueden dormir mis ojos', u'number': u'03', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 1/03 - Endechas y Canciones - I. no pueden dormir mis ojos.flac', u'length': 117170, u'acoustid': [u'30d5a563-b3a4-4dbf-b05c-dc60185b5b64']},
                      {u'sha1': u'188ff0222905b78b5ef65f55073a466090ca8e78', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Incantation', u'number': u'15', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 1/15 - Incantation.flac', u'length': 881360, u'acoustid': [u'd4ab478f-60f0-4888-b799-2bc5b9ea2454']},
                      {u'sha1': u'19661e4576f50e47c588a9ae5548461c62819130', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Anonymous: Adoro te devote', u'number': u'01', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 2/01 - Anonymous- Adoro te devote.flac', u'length': 40730, u'acoustid': [u'ae27ad93-ef4f-45d4-9418-25dc10e3cb34']},
                      {u'sha1': u'c56fe7bf41912af7920d5a2c8dc9fd0df5bd3b5b', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Michael Finnissy: Stabant autem iuxta crucem', u'number': u'07', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 2/07 - Michael Finnissy- Stabant autem iuxta crucem.flac', u'length': 171600, u'acoustid': [u'e7e740e2-b8e2-42a6-81be-daa3ed2b30b5']},
                      {u'sha1': u'78896613ec4ee9a679bb18ea0e436c3565cf68d7', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Arvo Part: Summa', u'number': u'04', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 2/04 - Arvo Part- Summa.flac', u'length': 324240, u'acoustid': [u'bae244e1-5278-48d7-97d9-0b12ed53ddb8']},
                      {u'sha1': u'e41970421a9fdbce223308a63589df03f60e95f0', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Ivan Moody: Canticum Canticorum I - III. Ego dilecto meo', u'number': u'11', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 2/11 - Ivan Moody- Canticum Canticorum I - III. Ego dilecto meo.flac', u'length': 104300, u'acoustid': [u'64a9f4ca-7cc0-4bb1-9c7f-297d6a57831a']},
                      {u'sha1': u'3ab11df259f7a6b5cd820a57f29b70da36211201', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Ivan Moody: Canticum Canticorum I - II. Descendi in hortum meum', u'number': u'10', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 2/10 - Ivan Moody- Canticum Canticorum I - II. Descendi in hortum meum.flac', u'length': 117020, u'acoustid': [u'2709a44f-c5ad-4afc-998b-6a7876b10bde']},
                      {u'sha1': u'cb2ce3b531bd0243d3ee7aa194c24a2bf1be4926', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Ivan Moody: Canticum Canticorum I - I. Surge, properea amica mea', u'number': u'09', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 2/09 - Ivan Moody- Canticum Canticorum I - I. Surge, properea amica mea.flac', u'length': 132800, u'acoustid': [u'10bfb000-5ec9-4795-ad3a-8aef74b3d058']},
                      {u'sha1': u'086c144d0c03e870c7cebc03fa313b0ef4b04f10', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'James MacMillan: ...here in hiding...', u'number': u'02', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 2/02 - James MacMillan- ...here in hiding....flac', u'length': 766220, u'acoustid': [u'9c92c7ba-2578-4315-be8a-cb1669a8cf24']},
                      {u'sha1': u'c1eff4c6b9c2af206ace3f57623f1fda0c027ee3', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Elizabeth Liddle: Whale Rant', u'number': u'05', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 2/05 - Elizabeth Liddle- Whale Rant.flac', u'length': 320130, u'acoustid': [u'dd85ba11-7712-4055-b077-fda7771e951f']},
                      {u'sha1': u'4bdcf0538b9b84824511f2797b0b8020505f90d9', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Arvo Part: And One Of The Pharisees...', u'number': u'03', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 2/03 - Arvo Part- And One Of The Pharisees....flac', u'length': 458330, u'acoustid': [u'f33135a7-4f3d-464a-bf7d-e51e510efccd']},
                      {u'sha1': u'9cf5ea24d23ee19f06e66b5eb07ac6ff3188c1cc', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'John Casken: Sharp Thorne', u'number': u'08', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 2/08 - John Casken- Sharp Thorne.flac', u'length': 420100, u'acoustid': [u'a45af8ab-cc86-4530-8e0d-2c09a6bc6811']},
                      {u'sha1': u'e100469186f9ca3f368272e06855b33a97b17dba', u'artist': u'Hilliard Ensemble', u'format': u'Flac', u'title': u'Joanne Metcalf: Music For The Star Of The Sea', u'number': u'06', u'filename': u'A Hilliard Songbook New Music for Voices FLAC/Disc 2/06 - Joanne Metcalf- Music For The Star Of The Sea.flac', u'length': 492490, u'acoustid': [u'3561f9c1-8d6d-4a42-be03-745e253735ad']}]
        }
        self.assertEqual(linked, expected)
