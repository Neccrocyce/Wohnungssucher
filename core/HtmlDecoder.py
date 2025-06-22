from __future__ import annotations
import re
import sys

# tag names of empty html elements (without end tag)
html_empty_elements = [
    '!DOCTYPE',
    '!doctype',
    '!Doctype',
    '!DocType',
    'area',
    'base',
    'br',
    'col',
    'embed',
    'hr',
    'img',
    'input',
    'link',
    'meta',
    'param',
    'source',
    'track',
    'wbr'
]

# tag names of html elements without children
html_element_wo_children = [
    'script',
    '!--'
]


class HtmlElement:
    """
    This class represents an HTML element
    """
    tag: str
    inner_html: str
    attributes: dict
    children: list[HtmlElement]
    parent: HtmlElement | None

    def __init__(self, tag: str, inner_html: str, attributes: dict = None, parent: HtmlElement | None = None):
        self.tag = tag
        self.inner_html = inner_html
        self.attributes = attributes
        self.children = []
        self.parent = parent

        if self.attributes is None:
            self.attributes = {}

    def add_child(self, tag: str, inner_html: str, attributes: dict):
        self.children.append(HtmlElement(tag, inner_html, attributes, self))

    def get_element_by_id(self, elem_id: str) -> HtmlElement | None:
        """
        :param elem_id: requested id
        :return: The HtmlElement with the id @elem_id or None if there does not exist a HtmlElement with that id
        """
        return self._get_element_by_id_recursive(elem_id, self)

    def _get_element_by_id_recursive(self, elem_id: str, html_element: HtmlElement) -> HtmlElement | None:
        if 'id' in html_element.attributes.keys():
            if html_element.attributes['id'] == elem_id:
                return html_element

        for child in html_element.children:
            html_elem = self._get_element_by_id_recursive(elem_id, child)
            if html_elem:
                return html_elem

        return None

    def get_elements_by_tag(self, tag: str) -> list[HtmlElement]:
        """
        :param tag: requested tag
        :return: list containing all HtmlElements with the tag @tag
        """
        return self._get_element_by_tag_recursive(tag, self)

    def _get_element_by_tag_recursive(self, tag: str, html_element: HtmlElement) -> list[HtmlElement]:
        html_elements_w_tag = []
        if html_element.tag == tag:
            html_elements_w_tag.append(html_element)

        for child in html_element.children:
            html_elements_w_tag += self._get_element_by_tag_recursive(tag, child)

        return html_elements_w_tag

    def get_elements_by_class(self, class_id: str) -> list[HtmlElement]:
        """
        :param class_id: requested class_id
        :return: list containing all HtmlElements with the class @class_id
        """
        return self._get_element_by_class_recursive(class_id, self)

    def _get_element_by_class_recursive(self, class_id: str, html_element: HtmlElement) -> list[HtmlElement]:
        html_elements_w_class = []
        if 'class' in html_element.attributes.keys():
            if html_element.attributes['class'] == class_id:
                html_elements_w_class.append(html_element)

        for child in html_element.children:
            html_elements_w_class += self._get_element_by_class_recursive(class_id, child)

        return html_elements_w_class

    def get_elements_by_inner_html(self, inner_html: str) -> list[HtmlElement]:
        """
        :param inner_html: requested inner html
        :return: list containing all HtmlElements with the inner html @inner_html
        """
        return self._get_element_by_inner_html_recursive(inner_html, self)

    def _get_element_by_inner_html_recursive(self, inner_html: str, html_element: HtmlElement) -> list[HtmlElement]:
        html_elements_w_inner = []
        if html_element.inner_html == inner_html:
            html_elements_w_inner.append(html_element)

        for child in html_element.children:
            html_elements_w_inner += self._get_element_by_inner_html_recursive(inner_html, child)

        return html_elements_w_inner

    def __str__(self):
        attr_list = [str(k) + '="' + str(v) + '"' for k, v in self.attributes.items()]
        attrs = ' '.join(attr_list)
        return f'<{self.tag} {attrs}>'

    def __repr__(self):
        return self.__str__()


class HtmlDocument:
    # list of all ids in the html document
    ids: list

    # string representing the html document
    content: str

    # extracted html document
    html_document: HtmlElement

    def __init__(self, content: str):
        """
        Take an html document as string and parse all HTML elements.
        If an HTML element does not end with the required end-tag. It will be considered as inner_html as well as all
        following HTML elements at the same level.
        :param content: string representing an html document
        """
        self.ids = []

        self.content = content

        # remove line breaks and tabs
        self.content = re.sub('[\n\r\t]', '', self.content)

        # replace <br> by \t (temporary. will later be replaced by \n)
        self.content = re.sub('<br>', '\t', self.content)

        # extract html
        self.html_document = HtmlElement('', self.content)
        self._extract_html(self.html_document)

        # create id list
        self._create_id_list(self.html_document)

    def _extract_html(self, html_element: HtmlElement):
        """
        Extract the html document, i.e., find all html elements as well as the inner-htmls and return a HtmlElement
        object which contains further HtmlElement objects as children
        :param html_element:
        """

        # check if html can have children
        if html_element.tag in html_element_wo_children:
            return

        children, inner_html_no_tag = self._find_all_html_elements(html_element.inner_html)
        html_element.inner_html = inner_html_no_tag
        html_element.children = children

        for child in html_element.children:
            child.parent = html_element
            self._extract_html(child)

    def _find_all_html_elements(self, content: str) -> tuple[list[HtmlElement], str]:
        """
        Find all html_elements in content as well as the inner_html
        :param content: The content in which is looked for the HTML elements
        :return: Tuple of a list containing all html elements as HtmlElement object and the inner html
        """
        html_elements = []
        while True:
            html_element_obj, start_tag, has_endtag = self._find_next_start_tag(content)
            if not html_element_obj:
                # replace \t to \n (<br> was replaced by \t before) and assign to inner_html
                inner_html = re.sub('\t', '\n', content)
                break

            # check if empty html element
            if html_element_obj.tag in html_empty_elements:
                has_endtag = False
                end_tag = ''
            else:
                end_tag = '</' + html_element_obj.tag + '>'

            # extract html element
            if has_endtag:
                html_elem = self._find_html_element(html_element_obj.tag, content, end_tag=end_tag)
                # if html end tag does not exist, no further decoding of html elements
                if not html_elem:
                    inner_html = re.sub('\t', '\n', content)
                    break
            else:
                html_elem = start_tag

            # extract inner html if html element is not a comment
            if html_element_obj.tag != '!--':
                inner_html_elem = re.sub('^' + re.escape(start_tag) + '|' + re.escape(end_tag) + '$', '', html_elem)
                html_element_obj.inner_html = inner_html_elem

            # remove html element from content
            content = content.replace(html_elem, '', 1)

            html_elements.append(html_element_obj)

        return html_elements, inner_html

    def _find_next_start_tag(self, content: str) -> tuple[HtmlElement | None, str, bool]:
        """
        Find the next html in content and extract its start-tag
        :param content: html document as string
        :return: HtmlElement representing the first occurrence of a html element,
                start-tag as string
                whether the start-tag is followed by an end-tag, i.e., not of the form: .../>
        """
        index_start = content.find('<')
        if index_start == -1:
            return None, '', False

        content = content[index_start + 1:]

        # find tag
        tag = re.findall('[^ />]*', content)
        if not tag:
            raise ValueError('Invalid syntax for html element, content: ' + content)
        tag = tag[0]

        # check if comment
        if tag.startswith('!--'):
            start_tag_str = re.findall('!--.*?-->', content)
            if not start_tag_str:
                raise ValueError("Comment never ends in content: " + content)

            start_tag_str = '<' + start_tag_str[0]
            comment = re.sub('^<!--|-->$', '', start_tag_str)
            return HtmlElement('!--', comment), start_tag_str, False

        content = re.sub('^' + re.escape(tag), '', content)

        # check if end
        if content[0] == '>':
            return HtmlElement(tag, ''), '<' + tag + '>', True
        elif content[0:1] == '/>':
            return HtmlElement(tag, ''), '<' + tag + '/>', False

        # find attributes
        in_string = False
        in_key = True
        tmp_key = ''
        tmp_value = ''
        attributes = {}
        start_tag_str = '<' + tag + content[0]

        content = content[1:]

        for c in content:
            start_tag_str += c
            # string starts or ends
            if c == '"':
                in_string = not in_string
                continue
            elif not in_string:
                # starttag ends
                if c == '>':
                    if start_tag_str[-2] == '/':
                        has_endtag = False
                        if in_key and tmp_key:
                            tmp_key = tmp_key[0:-1]
                        elif not in_key and tmp_value:
                            tmp_value = tmp_value[0:-1]
                    else:
                        has_endtag = True

                    attributes[tmp_key] = tmp_value
                    return HtmlElement(tag, '', attributes), start_tag_str, has_endtag
                # value of attribute starts
                elif c == '=':
                    in_key = False
                    continue
                # attribute ends
                elif c == ' ':
                    attributes[tmp_key]= tmp_value
                    in_key = True
                    tmp_key = ''
                    tmp_value = ''
                    continue

            if in_key:
                tmp_key += c
            else:
                tmp_value += c

        raise ValueError('Invalid syntax in html document')

    def _find_html_element(self, tag: str, content: str, end_tag: str | None = None) -> str | None:
        """
        Take a tag and the content and find the first occurrence of a html element with that tag
        :param tag: tag name of the HTML element to look for
        :param end_tag: End-tag of the HTML element to look for if it differs from the convention, i.e., not </tag>
        :param content: The content in which is looked for the HTML element
        :return: string representing the html element or None if there is no end-tag
        """
        start_tag_s_regex = '<' + re.escape(tag) + '[> ]'
        end_tag = '</' + tag + '>' if not end_tag else end_tag
        index_start = re.search(start_tag_s_regex, content)
        if index_start is None:
            raise ValueError('HTML element does not exist for tag: ' + tag)
        else:
            index_start = index_start.start()

        # find end tag
        num_open_tags = -1
        index_start_next = index_start
        index_end = index_start
        while True:
            index_end = content.find(end_tag, index_end + 1)
            if index_end == -1:
                content_short = content[index_start:99] if len(content[index_start:]) >= 100 else content[index_start:]
                print('WARNING: End-tag "' + end_tag + '" does not exist for content starting with: ' + content_short, file=sys.stderr)
                return None
            while -1 < index_start_next < index_end:
                # index_start_next = content.find(start_tag_s, index_start_next + 1)
                index_start_next_res = re.search(start_tag_s_regex, content[(index_start_next + 1):])
                if index_start_next_res is None:
                    index_start_next = -1
                else:
                    index_start_next += index_start_next_res.start() + 1

                num_open_tags += 1

            if num_open_tags == 0:
                break
            else:
                num_open_tags -= 1

        return content[index_start:index_end] + end_tag

    def _create_id_list(self, html_element: HtmlElement):
        """
        Create a list containing each id appearing in the html document with a reference to its HtmlElement object
        :param html_element: A HtmlElement object to look for the id
        :return: None
        """
        if 'id' in html_element.attributes.keys():
            self.ids.append({'id': html_element.attributes['id'], 'html_element': html_element})

        for child in html_element.children:
            self._create_id_list(child)

    def get_element_by_id(self, elem_id: str) -> HtmlElement | None:
        """
        :param elem_id: requested id
        :return: The HtmlElement with the id @elem_id or None if there does not exist a HtmlElement with that id
        """
        for elem in self.ids:
            if elem_id == elem["id"]:
                return elem['html_element']

        return None

    def get_elements_by_class(self, class_id: str) -> list[HtmlElement]:
        """
        :param class_id: requested class_id
        :return: list containing all HtmlElements with the class @class_id
        """
        return self.html_document.get_elements_by_class(class_id)

    def get_elements_by_tag(self, tag: str) -> list[HtmlElement]:
        """
        :param tag: requested tag
        :return: list containing all HtmlElements with the tag @tag
        """
        return self.html_document.get_elements_by_tag(tag)

    def get_elements_by_inner_html(self, inner_html: str) -> list[HtmlElement]:
        """
        :param inner_html: requested inner html
        :return: list containing all HtmlElements with the inner html @inner_html
        """
        return self.html_document.get_elements_by_inner_html(inner_html)

    def __str__(self):
        return str(self.content)
