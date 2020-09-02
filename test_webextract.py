import webextract
import pytest

@pytest.mark.parametrize("data_file, total_num, Spain_odd, Iceland_odd",
                         [('data/paddypower.com.html', 12*3, '15/2', '500/1')])
def test_paddy(data_file, total_num, Spain_odd, Iceland_odd):
    with open(data_file) as f:
        odds_data = webextract.PaddyPowerOdds(content = f.read())
    assert len(odds_data.odds) == len(odds_data.teams)
    assert len(odds_data.odds) == total_num
    d = dict(zip(odds_data.teams, odds_data.odds))
    assert d['Spain'] == Spain_odd
    assert d['Iceland'] == Iceland_odd

@pytest.mark.parametrize("data_file, total_num, Spain_odd, England_odd",
                         [('data/betfair.com.html', 25, '17/2', '11/2')])
def test_betfair(data_file, total_num, Spain_odd, England_odd):
    with open(data_file) as f:
        odds_data = webextract.BetFairOdds(content = f.read())
    assert len(odds_data.odds) == len(odds_data.teams)
    assert len(odds_data.odds) == total_num
    d = dict(zip(odds_data.teams, odds_data.odds))
    assert d['Spain'] == Spain_odd
    assert d['England'] == England_odd

