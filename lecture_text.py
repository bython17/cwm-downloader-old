global_styling = '''
body {
    color: #aaa;
    font-family: 'ubuntu', sans-serif;
    margin: 0;
    padding: 0;
}

#root {
    background-color: #111112;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
}

p {
    line-height: 2;
}

a {
    color: #289;
    text-decoration: none;
    font-weight: 300;
}

svg {
    display: none;
}

div[role="main"] {
    max-width: 800px;
    min-width: 400px;
    margin-top: 20px;
    height: fit-content;
}

div.lecture-attachment.lecture-attachment-type-pdf_embed, div.lecture-attachment.lecture-attachment-type-file {
    margin-top: 40px;
    border-radius: 10px;
    padding: 10px;
    background-color: #222;
}

div.lecture-attachment div.attachment {
    padding: 5px;
}

div.lecture-attachment a {
    color: #289;
    text-decoration: none;
    font-weight: 900;
}

h2.section-title {
    color: #444;
    font-size: 32px;
    margin-bottom: 10px;
}
'''


def get_main_element(lecture_soup, lecture_number):
    lecture_soup_c = lecture_soup
    main_element = lecture_soup_c.find(
        'div', {'role': 'main', 'class': 'course-mainbar'})
    main_element.find(
        'a', {'class': 'btn complete lecture-complete'}).decompose()
    main_element.find('div', {'id': 'empty_box'}).decompose()
    main_element.find('div', {'class': 'attachment-data'}).decompose()

    title = main_element.find('h2', {'class': 'section-title'}).text.strip()

    title_list = title.split('-')
    if title_list[0].isdigit():
        title_list[0] = str(lecture_number)
        new_title = '-'.join(title_list)
    else:
        new_title = f"{lecture_number}- {title}"

    main_element.find('h2', {'class': 'section-title'}).string = new_title

    main_element.find('meta').attrs = {}

    try:
        main_element.find('div', {
                          'class': 'row attachment-pdf-embed'}).decompose()
    except AttributeError:
        pass

    return main_element.prettify()


def create_html(lecture_name, element, styles=''):
    return f'''<html>
  <head>
  <title> {lecture_name} </title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap" rel="stylesheet">
  <style>
  {styles if styles else global_styling}
  </style>
  </head>
  <body>
  <div id="root">
  {element}
  </div>
  </body>
  </html>
  '''
