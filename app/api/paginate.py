from flask import url_for


def paginate(query, page, per_page, url):
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    items = pagination.items
    prev = None
    next_page = None
    if pagination.has_prev:
        prev = url_for(url, page=page+1)
    if pagination.has_next:
        next_page = url_for(url, page=page-1)
    return items, prev, next_page, pagination.total
