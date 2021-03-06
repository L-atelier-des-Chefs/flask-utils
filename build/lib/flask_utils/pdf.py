import os

import jinja2
import pdfkit
import tempfile

import config


def get_temp_path(local_prefix=""):
    return (
        f"{local_prefix}temp" if os.getenv("ENVIRONMENT", "dev") == "local" else "/tmp"
    )


def price(value):
    return "{}€".format(round(value / 100, 2))


def add_pdf_header(header_html, options, **kwargs):
    if header_html is None:
        return
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as header:
        options["header-html"] = header.name
        template_loader = jinja2.FileSystemLoader(searchpath="./assets")
        template_env = jinja2.Environment(loader=template_loader)
        header_template = template_env.get_template(header_html)
        header.write(header_template.render(**kwargs).encode("utf-8"))
    return


def add_pdf_footer(footer_html, options, **kwargs):
    if footer_html is None:
        return
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as footer:
        options["footer-html"] = footer.name
        template_loader = jinja2.FileSystemLoader(searchpath="./assets")
        template_env = jinja2.Environment(loader=template_loader)
        footer_template = template_env.get_template(footer_html)
        footer.write(footer_template.render(**kwargs).encode("utf-8"))
    return


def generate_pdf(
        template_file,
        file_name,
        header_html=None,
        footer_html=None,
        page_width="21cm",
        page_height="29.7cm",
        margin_top="2in",
        margin_bottom="0.75in",
        margin_x="0.75in",
        **kwargs,
):
    template_loader = jinja2.FileSystemLoader(searchpath="./assets")
    template_env = jinja2.Environment(loader=template_loader)
    template_env.filters["price"] = price
    main_template = template_env.get_template(template_file)
    main_content = main_template.render(**kwargs)

    file_path = f"{get_temp_path('./')}/{file_name}"

    html_path = f"{file_path}.html"
    html_file = open(html_path, "w")
    html_file.write(main_content)
    html_file.close()

    options = {
        "page-width": page_width,
        "page-height": page_height,
        "margin-top": margin_top,
        "margin-right": margin_x,
        "margin-bottom": margin_bottom,
        "margin-left": margin_x,
        "encoding": "UTF-8",
        "orientation": "Portrait",
        "dpi": 300,
        "no-outline": None,
        "no-stop-slow-scripts": True,
        "enable-local-file-access": True,
    }
    add_pdf_header(header_html, options, **kwargs)
    add_pdf_footer(footer_html, options, **kwargs)
    configuration = (
        pdfkit.configuration(wkhtmltopdf="/opt/bin/wkhtmltopdf")
        if config.WKHTMLTOPDF_PATH
        else pdfkit.configuration()
    )
    pdfkit.from_string(
        main_content, f"{file_path}.pdf", options=options, configuration=configuration
    )


def remove_files(filenames):
    for filename in filenames:
        path = get_temp_path(f"{os.path.abspath(os.getcwd())}/")
        os.remove(f"{path}/{filename}")
