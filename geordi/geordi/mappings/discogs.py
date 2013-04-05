# geordi
# Copyright (C) 2012 Ian McEwen, MetaBrainz Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division, absolute_import, unicode_literals

from geordi.mappings.util import collect_text, comma_list, collect_obj, base_mapping, MappingBase, unformat_track_length
from geordi.utils import uniq
import re

#cribbed from https://github.com/murdos/musicbrainz-userscripts/blob/master/discogs_importer.user.js
countries = {
    "Afghanistan": "AF",
    "Albania": "AL",
    "Algeria": "DZ",
    "American Samoa": "AS",
    "Andorra": "AD",
    "Angola": "AO",
    "Anguilla": "AI",
    "Antarctica": "AQ",
    "Antigua and Barbuda": "AG",
    "Argentina": "AR",
    "Armenia": "AM",
    "Aruba": "AW",
    "Australia": "AU",
    "Austria": "AT",
    "Azerbaijan": "AZ",
    "Bahamas": "BS",
    "Bahrain": "BH",
    "Bangladesh": "BD",
    "Barbados": "BB",
    "Belarus": "BY",
    "Belgium": "BE",
    "Belize": "BZ",
    "Benin": "BJ",
    "Bermuda": "BM",
    "Bhutan": "BT",
    "Bolivia": "BO",
    "Croatia": "HR",
    "Botswana": "BW",
    "Bouvet Island": "BV",
    "Brazil": "BR",
    "British Indian Ocean Territory": "IO",
    "Brunei Darussalam": "BN",
    "Bulgaria": "BG",
    "Burkina Faso": "BF",
    "Burundi": "BI",
    "Cambodia": "KH",
    "Cameroon": "CM",
    "Canada": "CA",
    "Cape Verde": "CV",
    "Cayman Islands": "KY",
    "Central African Republic": "CF",
    "Chad": "TD",
    "Chile": "CL",
    "China": "CN",
    "Christmas Island": "CX",
    "Cocos (Keeling) Islands": "CC",
    "Colombia": "CO",
    "Comoros": "KM",
    "Congo": "CG",
    "Cook Islands": "CK",
    "Costa Rica": "CR",
    "Virgin Islands, British": "VG",
    "Cuba": "CU",
    "Cyprus": "CY",
    "Czech Republic": "CZ",
    "Denmark": "DK",
    "Djibouti": "DJ",
    "Dominica": "DM",
    "Dominican Republic": "DO",
    "Ecuador": "EC",
    "Egypt": "EG",
    "El Salvador": "SV",
    "Equatorial Guinea": "GQ",
    "Eritrea": "ER",
    "Estonia": "EE",
    "Ethiopia": "ET",
    "Falkland Islands (Malvinas)": "FK",
    "Faroe Islands": "FO",
    "Fiji": "FJ",
    "Finland": "FI",
    "France": "FR",
    "French Guiana": "GF",
    "French Polynesia": "PF",
    "French Southern Territories": "TF",
    "Gabon": "GA",
    "Gambia": "GM",
    "Georgia": "GE",
    "Germany": "DE",
    "Ghana": "GH",
    "Gibraltar": "GI",
    "Greece": "GR",
    "Greenland": "GL",
    "Grenada": "GD",
    "Guadeloupe": "GP",
    "Guam": "GU",
    "Guatemala": "GT",
    "Guinea": "GN",
    "Guinea-Bissau": "GW",
    "Guyana": "GY",
    "Haiti": "HT",
    "Virgin Islands, U.S.": "VI",
    "Honduras": "HN",
    "Hong Kong": "HK",
    "Hungary": "HU",
    "Iceland": "IS",
    "India": "IN",
    "Indonesia": "ID",
    "Wallis and Futuna": "WF",
    "Iraq": "IQ",
    "Ireland": "IE",
    "Israel": "IL",
    "Italy": "IT",
    "Jamaica": "JM",
    "Japan": "JP",
    "Jordan": "JO",
    "Kazakhstan": "KZ",
    "Kenya": "KE",
    "Kiribati": "KI",
    "Kuwait": "KW",
    "Kyrgyzstan": "KG",
    "Lao People's Democratic Republic": "LA",
    "Latvia": "LV",
    "Lebanon": "LB",
    "Lesotho": "LS",
    "Liberia": "LR",
    "Libyan Arab Jamahiriya": "LY",
    "Liechtenstein": "LI",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Montserrat": "MS",
    "Macedonia, The Former Yugoslav Republic of": "MK",
    "Madagascar": "MG",
    "Malawi": "MW",
    "Malaysia": "MY",
    "Maldives": "MV",
    "Mali": "ML",
    "Malta": "MT",
    "Marshall Islands": "MH",
    "Martinique": "MQ",
    "Mauritania": "MR",
    "Mauritius": "MU",
    "Mayotte": "YT",
    "Mexico": "MX",
    "Micronesia, Federated States of": "FM",
    "Morocco": "MA",
    "Monaco": "MC",
    "Mongolia": "MN",
    "Mozambique": "MZ",
    "Myanmar": "MM",
    "Namibia": "NA",
    "Nauru": "NR",
    "Nepal": "NP",
    "Netherlands": "NL",
    "Netherlands Antilles": "AN",
    "New Caledonia": "NC",
    "New Zealand": "NZ",
    "Nicaragua": "NI",
    "Niger": "NE",
    "Nigeria": "NG",
    "Niue": "NU",
    "Norfolk Island": "NF",
    "Northern Mariana Islands": "MP",
    "Norway": "NO",
    "Oman": "OM",
    "Pakistan": "PK",
    "Palau": "PW",
    "Panama": "PA",
    "Papua New Guinea": "PG",
    "Paraguay": "PY",
    "Peru": "PE",
    "Philippines": "PH",
    "Pitcairn": "PN",
    "Poland": "PL",
    "Portugal": "PT",
    "Puerto Rico": "PR",
    "Qatar": "QA",
    "Reunion": "RE",
    "Romania": "RO",
    "Russian Federation": "RU",
    "Russia": "RU",
    "Rwanda": "RW",
    "Saint Kitts and Nevis": "KN",
    "Saint Lucia": "LC",
    "Saint Vincent and The Grenadines": "VC",
    "Samoa": "WS",
    "San Marino": "SM",
    "Sao Tome and Principe": "ST",
    "Saudi Arabia": "SA",
    "Senegal": "SN",
    "Seychelles": "SC",
    "Sierra Leone": "SL",
    "Singapore": "SG",
    "Slovenia": "SI",
    "Solomon Islands": "SB",
    "Somalia": "SO",
    "South Africa": "ZA",
    "Spain": "ES",
    "Sri Lanka": "LK",
    "Sudan": "SD",
    "Suriname": "SR",
    "Swaziland": "SZ",
    "Sweden": "SE",
    "Switzerland": "CH",
    "Syrian Arab Republic": "SY",
    "Tajikistan": "TJ",
    "Tanzania, United Republic of": "TZ",
    "Thailand": "TH",
    "Togo": "TG",
    "Tokelau": "TK",
    "Tonga": "TO",
    "Trinidad and Tobago": "TT",
    "Tunisia": "TN",
    "Turkey": "TR",
    "Turkmenistan": "TM",
    "Turks and Caicos Islands": "TC",
    "Tuvalu": "TV",
    "Uganda": "UG",
    "Ukraine": "UA",
    "United Arab Emirates": "AE",
    "UK": "GB",
    "US": "US",
    "United States Minor Outlying Islands": "UM",
    "Uruguay": "UY",
    "Uzbekistan": "UZ",
    "Vanuatu": "VU",
    "Vatican City State (Holy See)": "VA",
    "Venezuela": "VE",
    "Viet Nam": "VN",
    "Western Sahara": "EH",
    "Yemen": "YE",
    "Zambia": "ZM",
    "Zimbabwe": "ZW",
    "Taiwan": "TW",
    "[Worldwide]": "XW",
    "Europe": "XE",
    "Soviet Union (historical, 1922-1991)": "SU",
    "East Germany (historical, 1949-1990)": "XG",
    "Czechoslovakia (historical, 1918-1992)": "XC",
    "Congo, The Democratic Republic of the": "CD",
    "Slovakia": "SK",
    "Bosnia and Herzegovina": "BA",
    "Korea (North), Democratic People's Republic of": "KP",
    "North Korea": "KP",
    "Korea (South), Republic of": "KR",
    "South Korea": "KR",
    "Montenegro": "ME",
    "South Georgia and the South Sandwich Islands": "GS",
    "Palestinian Territory": "PS",
    "Macao": "MO",
    "Timor-Leste": "TL",
    "Åland Islands": "AX",
    "Guernsey": "GG",
    "Isle of Man": "IM",
    "Jersey": "JE",
    "Serbia": "RS",
    "Saint Barthélemy": "BL",
    "Saint Martin": "MF",
    "Moldova": "MD",
    "Yugoslavia (historical, 1918-2003)": "YU",
    "Serbia and Montenegro (historical, 2003-2006)": "CS",
    "Côte d'Ivoire": "CI",
    "Heard Island and McDonald Islands": "HM",
    "Iran, Islamic Republic of": "IR",
    "Saint Pierre and Miquelon": "PM",
    "Saint Helena": "SH",
    "Svalbard and Jan Mayen": "SJ"
}

class discogs(MappingBase):
    def link_types(self):
        return {
            'artist': {
                'name': "artist id",
                'key': 'artist_id',
                'type': ['artist']
            },
            'label': {
                'name': "label id",
                'key': 'label_id',
                'type': ['label']
            },
            'master': {
                'name': "master id",
                'key': 'master_id',
                'type': ['master']
            },
            'version': 1
        }

    def code_url(self):
        return self.code_url_pattern().format('discogs')

    def extract_linked(self, data):
        artists = labels = masters = []
        try:
            artists = [{'artist_id': artist['id']['text'], 'name': artist['name']['text']} for artist in collect_obj(data['discogs']['artist'])]
        except: pass

        try:
            labels = [{'label_id': label['id']['text'], 'name': label['name']['text']} for label in collect_obj(data['discogs']['label'])]
        except: pass

        try:
            masters = [{'master_id': master['_id'], 'title': master['title']['text']} for master in collect_obj(data['discogs']['master'])]
        except: pass

        return {u'artist': artists, u'label': labels, u'master': masters, 'version': 3}

    def automatic_item_matches(self, data):
        return {}

    def automatic_subitem_matches(self, data):
        return {}

    def map(self, data):
        target = base_mapping('release')
        target['version'] = 9
        release = target['release']

        try:
            release['title'] = collect_text(data['discogs']['release']['title'])
        except: pass

        try:
            release['date'] = collect_text(data['discogs']['release']['released'])
        except: pass

        try:
            release['country'] = [countries.get(country) for country in collect_text(data['discogs']['release']['country']) if countries.get(country, False)]
        except: pass

        try:
            release['artist'] = [{'name': artist['name']['text'], 'subitem': 'artist-{0}'.format(int(artist['id']['text']))} for artist in collect_obj(data['discogs']['release']['artists']['artist'])]
            release['combined_artist'] = comma_list([artist['name'] for artist in release['artist']])
        except: pass

        try:
            release['urls'] = [{'url': image['_uri'], 'type': 'cover art'} for image in collect_obj(data['discogs']['release']['images']['image'])]
        except: pass

        try:
            tracks = collect_obj(data['discogs']['release']['tracklist']['track'])
            for track in tracks:
                obj = {'title': collect_text(track['title'])}
                if 'artists' in track:
                    obj['artist'] = [{'name': artist['name']['text'], 'subitem': 'artist-{0}'.format(int(artist['id']['text']))} for artist in collect_obj(track['artists']['artist'])]
                else:
                    obj['artist'] = release['artist']
                obj['length_formatted'] = collect_text(track['duration'])
                obj['length'] = [unformat_track_length(a) for a in collect_text(track['duration'])]
                obj['number'] = collect_text(track['position'])
                release['tracks'].append(obj)
        except: pass

        return target
