def check_score(number):
    if number >=80:
          return True

    return False


def check_for_title(title_query, books):

    if title_query is not None:
        for book in books:
            if title_query not in book.title:
                books.remove(book)

    return books


