import sys
import json
import pytest

import main


def test_run_without_args(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['main.py'])
    with pytest.raises(SystemExit):
        main.main()


def test_run_with_invalid_args(monkeypatch, capfd):
    monkeypatch.setattr(sys, 'argv', ['main.py', 'invalid.csv'])
    main.main()
    captured = capfd.readouterr()
    assert captured.out == 'No such file or directory.\n'


def test_calculate_payout():
    pattern = r'hourly_rate|rate|salary'
    for key in ['hourly_rate', 'rate', 'salary']:
        employe = {key: 60, 'hours_worked': 150}
        assert main.calculate_payout(pattern, employe)


def test_calculate_payout_with_missing_field(capfd):
    pattern = r'income'
    employe = {'rate': 60, 'hours_worked': 150}
    assert main.calculate_payout(pattern, employe) == 0
    captured = capfd.readouterr()
    assert captured.out == 'Rate field is missing.\n'


def test_calculate_payout_with_invalid_field(capfd):
    pattern = r'hourly_rate|rate|salary'
    employe = {'rate': 'a', 'hours_worked': 150}
    assert main.calculate_payout(pattern, employe) == 0
    captured = capfd.readouterr()
    assert captured.out == 'Invalid field type.\n'


def test_search_for_field():
    pattern = r'hourly_rate|rate|salary'
    for key in ['hourly_rate', 'rate', 'salary']:
        employe = {key: 60}
        assert main.search_for_field(pattern, employe) == key

    
def test_search_for_field_with_invalid_field():
    pattern = r'income'
    employe = {'rate': 'a', 'hours_worked': 150}
    assert main.search_for_field(pattern, employe) == ''


def test_populate_fields():
    input_fields = ['id', 'email', 'name', 'department', 'hours_worked', 'rate']
    input_data = ['1', 'example@mail.ru', 'momo', 'design', '50', '50']
    output = main.populate_fields(input_fields, input_data)
    assert isinstance(output, dict)
    assert output['id'] == '1'
    assert output['email'] == 'example@mail.ru'
    assert output['name'] == 'momo'
    assert output['department'] == 'design'
    assert output['hours_worked'] == '50'
    assert output['rate'] == '50'


def test_populate_fields_with_mixed_fields():
    input_fields = ['email', 'name', 'department', 'hours_worked', 'salary', 'id']
    input_data = ['example@mail.ru', 'momo', 'design', '50', '50', '1']
    output = main.populate_fields(input_fields, input_data)
    assert isinstance(output, dict)
    assert output['name'] == 'momo'
    assert output['email'] == 'example@mail.ru'
    assert output['department'] == 'design'
    assert output['hours_worked'] == '50'
    assert output['salary'] == '50'
    assert output['id'] == '1'


def test_parse_csv():
    input_str = 'email,name,department,hours_worked,salary,id\n'
    output = main.parse_csv(input_str)
    assert isinstance(output, list)
    assert isinstance(output[0], str)
    assert len(output) == 6
    assert output[-1] == 'id'


def test_parse_csv_with_empty_line(capfd):
    input_str = ''
    output = main.parse_csv(input_str)
    assert isinstance(output, list)
    assert len(output) == 0
    captured = capfd.readouterr()
    assert captured.out == 'Line is empty.\n'


def test_write_to_json(tmp_path):
    employees = [
        {'id': 1, 'email': 'example@mail.ru', 'name': 'momo', 'department': 'design', 'hours_worked': '160', 'rate': '50'},
        {'id': 2, 'email': 'example2@mail.ru', 'name': 'yoyo', 'department': 'marketing', 'hours_worked': '140', 'rate': '60'},
        {'id': 3, 'email': 'example3@mail.ru', 'name': 'popo', 'department': 'design', 'hours_worked': '120', 'rate': '40'},
    ]
    path = tmp_path / 'output.json'
    main.write_to_json(path, employees)

    with open(path, 'r') as file:
        data = json.load(file)
        assert data == employees
