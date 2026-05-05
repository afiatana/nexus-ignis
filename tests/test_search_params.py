from web.search_service import normalize_search_params


def test_normalize_search_params_defaults():
    params = normalize_search_params('  link rot  ')

    assert params.query == 'link rot'
    assert params.page == 1
    assert params.page_size == 20
    assert params.category is None
    assert params.domain is None
    assert params.year is None


def test_normalize_search_params_filters_and_pagination():
    params = normalize_search_params(
        query='archive',
        category='News',
        domain='Example.COM',
        year='2024',
        page='3',
        page_size='10',
    )

    assert params.category == 'News'
    assert params.domain == 'example.com'
    assert params.year == 2024
    assert params.page == 3
    assert params.page_size == 10
    assert params.offset == 20


def test_normalize_search_params_caps_page_size():
    params = normalize_search_params('archive', page_size='999')

    assert params.page_size == 50


def test_normalize_search_params_ignores_invalid_year():
    params = normalize_search_params('archive', year='not-a-year')

    assert params.year is None
