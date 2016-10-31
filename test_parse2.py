from parse2 import *
from unittest.mock import patch, MagicMock
import types
def noop(): pass    

def test_is_blank():
    assert is_blank("") is True
    assert is_blank("  ") is True
    assert is_blank(" not blank ") is False


def test_activity_through():
    assert activity_through('nonsense') is None
    assert activity_through('Activity through February 20, 2015') == 'February 20, 2015'


def test_set_value():
    test_d = {}
    set_value('sample', 'hey', d=test_d)
    assert test_d['sample'] == 'hey'


@patch('parse2.set_value')
def test_set_prop_if_result_is_not_none(mock):
    func = lambda x: x
    line = 'hey'
    assert set_prop_if('test', func, line) is True
    assert mock.called
    mock.assert_called_with('test', 'hey')


@patch('parse2.set_value')
def test_set_prop_if_result_is_none(mock):
    func = lambda x: None
    line = 'hey'
    assert set_prop_if('test', func, line) is False
    assert mock.called is False


def test_line_search_returns_a_function():
    assert isinstance(line_search('test', noop), types.FunctionType)


def test_owner_name():
    line = "Owner name: 120 E. 102 ST. LLC                                                   120 E. 102 ST. LLC"
    assert owner_name(line) == "120 E. 102 ST. LLC"
    assert owner_name("property tax bill") is None

def test_property_address():
    line = "Property address: 213 W. 35TH ST.                                                213 W. 35TH ST."
    assert property_address(line) == "213 W. 35TH ST."
    assert owner_name("property tax bill") is None
    
def test_boro_block_lot():
    line = "Borough, block & lot: MANHATTAN (1), 00785, 0029           NEW YORK , NY 10001-1903"
    assert boro_block_lot(line) == "MANHATTAN (1), 00785, 0029"
    assert boro_block_lot("213 W. 35TH ST.") is None

def test_previous_charges():
     line = "Previous charges                                                                                           $419,024.70"
     assert previous_charges(line) == "$419,024.70"
     assert previous_charges("213 W. 35TH ST.") is None

def test_amount_paid():
    line = "Amount paid                                                                         $-419,024.70"
    assert amount_paid(line) == "$-419,024.70"
    assert amount_paid("previous charges           $1") is None

def test_interest():
     line = "Interest                                                                                                        $0.00"
     assert interest(line) == "$0.00"
     assert interest('Total previous charges including interest and payments') is None

def unpaid_charges():
    line = "Unpaid charges, if any                                                 $0.00"
    assert unpaid_charges(line) == "$0.00"
    assert unpaid_charges('Total previous charges including interest and payments') is None

def test_mailing_address():
      lines = [ "Mailing address:\n",
                "Owner name: 213 WEST 35TH ST. ASSOCIATES, L.P.                                   213 WEST 35TH ST. ASSOCIATES, L.P.\n",
                "Property address: 213 W. 35TH ST.                                                213 W. 35TH ST.\n",
                "Borough, block & lot: MANHATTAN (1), 00785, 0029                                 NEW YORK , NY 10001-1903\n",
                "\n"  ]
      assert mailing_address(lines) == "213 WEST 35TH ST. ASSOCIATES, L.P.\n213 W. 35TH ST.\nNEW YORK , NY 10001-1903"
      assert mailing_address(['blah\n', '\n', '\n']) is None

