
// Initialize toolbars
$(document).ready(function (){
    var i, target;
    target = $("textarea.markup-markdown");
    for (i = 0; i<target.length ; i++) {
        attach_toolbar($(target[i]), MARKDOWN_name);
    }
    target = $("textarea.markup-bbcode");
    for (i = 0; i<target.length ; i++) {
        attach_toolbar($(target[i]), BBCODE_name);
    }
});



//////////////////////////////////////////////

function getSelectedTextWithin(el) {
    // Return the text that is currently selected in given element
    var selectedText = "";
    if (typeof window.getSelection != "undefined") {
        var sel = window.getSelection(), rangeCount;
        if ( (rangeCount = sel.rangeCount) > 0 ) {
            var range = document.createRange();
            for (var i = 0, selRange; i < rangeCount; ++i) {
                range.selectNodeContents(el);
                selRange = sel.getRangeAt(i);
                if (selRange.compareBoundaryPoints(range.START_TO_END, range) == 1 && selRange.compareBoundaryPoints(range.END_TO_START, range) == -1) {
                    if (selRange.compareBoundaryPoints(range.START_TO_START, range) == 1) {
                        range.setStart(selRange.startContainer, selRange.startOffset);
                    }
                    if (selRange.compareBoundaryPoints(range.END_TO_END, range) == -1) {
                        range.setEnd(selRange.endContainer, selRange.endOffset);
                    }
                    selectedText += range.toString();
                }
            }
        }
    } else if (typeof document.selection != "undefined" && document.selection.type == "Text") {
        var selTextRange = document.selection.createRange();
        var textRange = selTextRange.duplicate();
        textRange.moveToElementText(el);
        if (selTextRange.compareEndPoints("EndToStart", textRange) == 1 && selTextRange.compareEndPoints("StartToEnd", textRange) == -1) {
            if (selTextRange.compareEndPoints("StartToStart", textRange) == 1) {
                textRange.setEndPoint("StartToStart", selTextRange);
            }
            if (selTextRange.compareEndPoints("EndToEnd", textRange) == -1) {
                textRange.setEndPoint("EndToEnd", selTextRange);
            }
            selectedText = textRange.text;
        }
    }
    return selectedText;
};


function get_suitable_quote(pos, text) {
    /* Given a position and a text, return the position of the most nested quote such that
     the start of this quote is before given position, and its end is after given position. */
    var quotes_re = /(\[quote(=.+?)?\])|(\[\/quote\])/g;
    var quotes = new Array();   // Array of starting positions

    while ((match = quotes_re.exec(text)) != null) {
        // First quote after our position
        if (pos <= match.index) {
            // Are we inside a non-closed [quote]?
            if (quotes.length > 0) {
                /* Change to quotes.length == 1 if you don't want to split quotes whose depth is > 1. */
                return quotes[quotes.length - 1];
            } else {
                return -1;
            }
        }

        // [/quote] found
        if (match[0].indexOf("/") > 0) {
            if (quotes.length > 0) {
                // Remove the associated starting [quote]
                quotes.pop();
            } else {
                return -1;
            }
        } else { // [quote] found
            quotes.push(match.index);
        }
    }

    return -1;
};


function bbcode_quote_handler(target, event, lastKeyWasEnter) {
    /* Split a [quote] block (if it exists) in two parts on double enter */
    if (event.keyCode != 13) {
        return false;
    } else {
        target = target.get()[0];

        var pos = target.selectionStart;
        var text = target.value;
        var quote_pos = get_suitable_quote(pos, text);
        if (quote_pos >= 0) {
            if (!lastKeyWasEnter) {
                return true;
            } else {
                var opening_tag = text.slice(quote_pos, text.indexOf("]", quote_pos) + 1);
                var closing_tag = "[/quote]";
                var text_prefix = text.substring(0, pos - 1);
                var text_suffix = text.substring(pos, text.length);

                target.value = text_prefix + closing_tag + "\n\n\n\n" + opening_tag + text_suffix;
                target.selectionStart = pos + closing_tag.length + 1;
                target.selectionEnd = pos + closing_tag.length + 1;

                return false;
            }
        } else {
            return false;
        }
    }
};


function board_add_quote(messageid, url, target) {
    /* Quote message #messageid in given target.
    Message retrieval endpoint must be specified using `url`.
     */
    function prepare_quoted_text(author, text) {
        var message = "[quote="+author["username"]+"]\n"+text+"\n[/quote]\n\n\n";
        // Do not copy img and embed objects.
        var regex1 = new RegExp("\\[img\\](.+)\\[/img\\]", "g");
        var regex2 = new RegExp("\\[embed\\](.+)\\[/embed\\]", "g");
        message = message.replace(regex1, "[url]$1[/url]");
        message = message.replace(regex2, "[url]$1[/url]");
        return message;
    }

    // Check if there is a selection in current message
    var text = getSelectedTextWithin($("#"+messageid).get()[0]);

    $.get(url)
        .done(function(data) {
            target = $(target);
            var message;

            // Use the selected text if any, or the whole message otherwhise
            if (text.length > 0) {
                message = prepare_quoted_text(data['author'], text);
            } else {
                message = prepare_quoted_text(data['author'], data['text']);
            }
            target.val(target.val() + message);
        });
};


function preview_markup(url, source_text, target_element) {
    var text=source_text;

    $(target_element).html("<p class='text-center'><span class='fa fa-spinner fa-spin'/></p>");

    $.post(url, {content: text})
        .done(function(data) {
            target_element.html(data);
            refresh_oembed(target_element);
        })
        .fail(function(data) {
            target_element.html("<strong>Erreur lors du chargement de la prévisualisation.</strong>");
        });

};


function markup_proceed(tag, target) {
    // Get DOM element
    target = target.get()[0];

    // Get target's selection
    var sel_start = target.selectionStart;
    var sel_end = target.selectionEnd;
    var is_selected = (sel_end - sel_start > 0);

    // Get text
    var text = target.value;
    var text_before = text.substring(0, sel_start);
    var text_inside = text.substring(sel_start, sel_end);
    var text_after = text.substring(sel_end);

    // Set text
    var new_text = text_before;
    if (tag.before) { new_text = new_text + tag.before; }
    new_text = new_text + text_inside;
    if (tag.after) { new_text = new_text + tag.after; }
    new_text = new_text + text_after;
    target.value = new_text;

    // Set position
    var new_position;
    if (tag.cursor.position == 'before') {
        new_position = Math.max(0, sel_start + tag.cursor.offset);
    } else {
        new_position = Math.min(new_text.length, text_before.length + tag.before.length + text_inside.length + tag.after.length - tag.cursor.offset);
    }
    target.selectionStart = target.selectionEnd = new_position;
    target.focus();
};


function get_markup_toolbar(markup, target) {
    var html;
    var toolbar;
    var buttons;

    if (markup == BBCODE_name) {
        toolbar = [
            ['bold', 'underline', 'italic', 'strike'],
            ['color', 'font', 'size', 'align'],
            ['quote', 'spoiler', 'code'],
            ['url', 'img', 'embed'],
        ];
    } else if (markup == MARKDOWN_name) {
        toolbar = [
            ['h1', 'h2', 'h3'],
            ['bold', 'italic'],
            ['quote', 'code', 'list'],
            ['url', 'image', 'embed'],
        ];
    } else {
        return false;
    }

    function add_tooltip(link, text) {
        link.attr("data-toggle", "tooltip");
        link.attr("data-placement", "top");
        link.attr("title", text);
        link.tooltip({container: 'body'});
    }

    function get_button(target, markup, action) {
        var link = $('<a>', {class: "btn btn-default"});
        link.click({markup:markup, action:action, target:target}, function(e) {
            markup_proceed(MARKUP[e.data.markup][e.data.action], e.data.target);
        });
        add_tooltip(link, MARKUP[markup][action].desc+"\n"+MARKUP[markup][action].syntaxe);

        var span;
        if (MARKUP[markup][action].icon) {
            span = $('<span>', {class: "fa "+MARKUP[markup][action].icon});
        } else if (MARKUP[markup][action].label) {
            span = $('<span>', {text: MARKUP[markup][action].label});
        } else {
            span = $('<span>', {text: "?"});
        }
        link.append(span);

        return link;
    }

    function get_button_group(target, markup, group) {
        var i;
        inner_div = $("<div>", {class:"btn-group btn-group-sm"});
        for (i=0; i<group.length; i++) {
            inner_div.append(get_button(target, markup, group[i]));
        }
        return inner_div;
    }

    html = $('<div>', {class:"markup-toolbar btn-toolbar"});

    // Add buttons
    var i;
    for (i = 0; i < toolbar.length; i++) {
        html.append(get_button_group(target, markup, toolbar[i]));
    }


    // If BBCode, add smileys
    if (markup == BBCODE_name) {
        function get_smiley_html(target) {
            var html = $("<div>", {class: "smiley-popup"});
            for (var i=0; i<SMILEY_LIST.length; i++) {
                var elem = $("<a>", {class:"btn btn-xs"});
                elem.click({smiley:SMILEY_LIST[i], target:target}, function(e){
                    markup_proceed(get_smiley_tag(e.data.smiley), e.data.target);
                });
                elem.append($("<img>", {src:SMILEY_URL+SMILEY_LIST[i]+".gif", title:":"+SMILEY_LIST[i]+":"}));
                html.append(elem);
            }
            return html;
        }

        var div = $("<div>", {class: "btn-group btn-group-sm"});
        var link = $("<a>", {class:"btn btn-default"});
        add_tooltip(link, "Liste des smileys");

        link.click({target:target}, function(e) {
            var smiley = e.data.target.prev(".smiley-popup").get(0);
            if (! smiley) {
                html = get_smiley_html(e.data.target);
                html.css("position", "absolute");
                e.data.target.before(html);
            } else {
                $(smiley).remove();
            }
        });

        link.append($("<span>", {class: "fa fa-smile-o"}));

        div.append(link);
        div.append(get_button(target, markup, 'sign'));
        html.append(div);
    }

    // Add preview
    var div = $("<div>", {class:"btn-group btn-group-sm"});
    var link = $("<a>", {class: "btn btn-default"});
    link.click({target:target, markup:markup}, function(e) {
        // Get first preview div, if any
        var preview = e.data.target.next(".markup-preview").get(0);
        if (preview) {
            // Remove preview and display target
            $(preview).remove();
            e.data.target.removeClass("hidden");
        } else {
            // Hide target and add preview div
            var div = $("<div>", {class: "markup-preview"});
            div.css('min-height', target.css("height"));
            div.css('max-height', target.css('height'));
            div.css('overflow', 'auto');
            e.data.target.addClass("hidden");
            e.data.target.after(div);
            preview_markup(MARKUP_URL.preview[e.data.markup], e.data.target.val(), div);
        }
    });
    link.append($("<span>", {class: "fa fa-eye"}));
    add_tooltip(link, "Prévisualisation");
    div.append(link);

    html.append(div);


    // Add help button
    var div = $("<div>", {class:"btn-group btn-group-sm"});
    var link = $("<a>", {class: "btn btn-default"});
    link.attr("href", MARKUP_URL.help[markup])
    add_tooltip(link, "Aide sur "+markup)
    link.attr("target", "new");
    link.append($("<span>", {class: "fa fa-question"}));
    div.append(link);
    html.append(div);

    return html;
};


function attach_toolbar(target, markup_name) {
    if (markup_name == BBCODE_name) {
        // Handler for "open quote on double enter"
        var handler = function (event) {
            this.lastKeyWasEnter = bbcode_quote_handler(target, event, this.lastKeyWasEnter);
        };
        $(target).keyup(handler);
    } else if (markup_name == MARKDOWN_name) {
        // Nothing special
    } else {
        return false;
    }

    // Add toolbar
    target.before(get_markup_toolbar(markup_name, target));
};


function get_smiley_tag(smiley) {
    return {'before': '',
        'after': ":"+smiley+": ",
        'cursor': { 'position': 'after', 'offset': 0}};
};






SMILEY_LIST = ['angel', 'angel2', 'angry', 'angry2', 'angry3', 'applause', 'approve', 'asleep', 'bad', 'bat', 'bawling', 'bawling2', 'bigsmile', 'bigsmile2', 'blind', 'blush', 'boolay', 'brave', 'broken', 'bunny', 'clown', 'confused', 'dark', 'devil', 'disgust', 'door', 'door2', 'evil', 'fail', 'frightened', 'fuck', 'fuckbroken', 'fucklaugh', 'fucktongue', 'heart', 'hello', 'help', 'innocent', 'innocent2', 'innocent3', 'jap', 'juggler', 'kc', 'kc2', 'kiss', 'kiss2', 'kiss3', 'kiss4', 'kiss5', 'lol', 'lol2', 'love', 'mad', 'mad2', 'mad3', 'masturbator', 'metal', 'moaner', 'mocker', 'no', 'odd', 'old', 'old2', 'pirate', 'pompomgirl', 'poppet', 'puke', 'quiet', 'reproving', 'sad', 'sad2', 'satisfy', 'sex', 'showoff', 'showoff2', 'slave', 'smile', 'stupid', 'surprised', 'tired', 'tongue', 'tongue2', 'tongue3', 'up', 'upset', 'wall', 'wink', 'yes', 'yes2', 'yes3', 'yes4', 'yum'];


SMILEY_URL = URL_PREFIX + "/static/images/smiley/";

BBCODE_name = "bbcode";
MARKDOWN_name = 'markdown';

MARKUP_URL = {
    'preview': {
        'bbcode': URL_PREFIX + "/markup/bbcode/preview/",
        'markdown': URL_PREFIX + "/markup/markdown/preview/"
    },
    'help': {
        'bbcode': URL_PREFIX + "/markup/bbcode/",
        'markdown': URL_PREFIX + "/markup/markdown/"
    }
}

MARKUP =  {
    'bbcode': {
        'bold': {
            'desc': 'Mettre en gras',
            'syntaxe': '[b]texte[/b]',
            'icon': 'fa-bold',
            'before': '[b]',
            'after': '[/b]',
            'cursor': {
                'position': 'after',
                'offset': 4
            }
        },
        'underline': {
            'desc': 'Souligner',
            'syntaxe': '[u]texte[/u]',
            'icon': 'fa-underline',
            'before': '[u]',
            'after': '[/u]',
            'cursor': {
                'position': 'after',
                'offset': 4
            }
        },
        'italic': {
            'desc': 'Mettre en italique',
            'syntaxe': '[i]texte[/i]',
            'icon': 'fa-italic',
            'before': '[i]',
            'after': '[/i]',
            'cursor': {
                'position': 'after',
                'offset': 4
            }
        },
        'strike': {
            'desc': 'Barrer',
            'syntaxe': '[strike]texte[/strike]',
            'icon': 'fa-strikethrough',
            'before': '[strike]',
            'after': '[/strike]',
            'cursor': {
                'position': 'after',
                'offset': 9
            }
        },
        'color': {
            'desc': 'Mettre en couleur',
            'syntaxe': '[color=red]texte[/color]',
            'icon': 'fa-flask',
            'before': '[color=]',
            'after': '[/color]',
            'cursor': {
                'position': 'before',
                'offset': 7
            }
        },
        'font': {
            'desc': 'Changer la police',
            'syntaxe': '[font=Helvetica]texte[/font]',
            'icon' : 'fa-font',
            'before': '[font=]',
            'after': '[/font]',
            'cursor': {
                'position': 'before',
                'offset': 6
            }
        },
        'size': {
            'desc': 'Changer la taille',
            'syntaxe': '[size=12pt]texte[/size]',
            'icon': 'fa-text-height',
            'before': '[size=]',
            'after': '[/size]',
            'cursor': {
                'position': 'before',
                'offset': 6
            }
        },
        'align': {
            'desc': 'Changer l\'alignement',
            'syntaxe': '[align=center]texte[/align]',
            'icon': 'fa-align-center',
            'before': '[align=]',
            'after': '[/align]',
            'cursor': {
                'position': 'before',
                'offset': 7
            }
        },
        'url': {
            'desc': 'Lien',
            'syntaxe': '[url]http://[/url] ou [url=http://]texte[/url]',
            'icon': 'fa-link',
            'before': '[url]',
            'after': '[/url]',
            'cursor': {
                'position': 'after',
                'offset': 6
            }
        },
        'img': {
            'desc': 'Insérer une image',
            'syntaxe': '[img]http://[/img]',
            'icon': 'fa-picture-o',
            'before': '[img]',
            'after': '[/img]',
            'cursor': {
                'position': 'after',
                'offset': 6
            }
        },
        'embed': {
            'desc': 'Intégrer un contenu',
            'syntaxe': '[embed]http://[/embed]',
            'icon': 'fa-video-camera',
            'before': '[embed]',
            'after': '[/embed]',
            'cursor': {
                'position': 'after',
                'offset': 8
            }
        },
        'sign': {
            'desc': 'Panneau smiley',
            'syntaxe': '[sign=smiley]texte[/sign]',
            'icon': 'fa-comment-o',
            'before': '[sign=]',
            'after': '[/sign]',
            'cursor': {
                'position': 'before',
                'offset': 6
            }
        },
        'spoiler': {
            'desc': 'Masquer le texte',
            'syntaxe': '[spoiler]texte[/spoiler]',
            'icon': 'fa-eraser',
            'before': '[spoiler]',
            'after': '[/spoiler]',
            'cursor': {
                'position': 'after',
                'offset': 10
            }
        },
        'code': {
            'desc': 'Code',
            'syntaxe': '[code]texte[/code]',
            'icon': 'fa-code',
            'before': '[code]',
            'after': '[/code]',
            'cursor': {
                'position': 'after',
                'offset': 7
            }
        },
        'quote': {
            'desc': 'Citation',
            'syntaxe': '[quote]texte[/quote] ou [quote=auteur]texte[/quote]',
            'icon': 'fa-quote-right',
            'before': '[quote]',
            'after': '[/quote]',
            'cursor': {
                'position': 'after',
                'offset': 8
            }
        },
    },
    'markdown': {
        'h1': {
            'desc': 'Titre 1',
            'syntaxe': '# Titre',
            'label': 'H1',
            'before': '# ',
            'after': '',
            'cursor': {
                'position': 'after',
                'offset': 0
            }
        },
        'h2': {
            'desc': 'Titre 2',
            'syntaxe': '## Titre',
            'label': 'H2',
            'before': '## ',
            'after': '',
            'cursor': {
                'position': 'after',
                'offset': 0
            }
        },
        'h3': {
            'desc': 'Titre 3',
            'syntaxe': '### Titre',
            'label': 'H3',
            'before': '### ',
            'after': '',
            'cursor': {
                'position': 'after',
                'offset': 0
            }
        },
        'bold': {
            'desc': 'Mettre en gras',
            'syntaxe': '**texte**',
            'icon': 'fa-bold',
            'before': '**',
            'after': '**',
            'cursor': {
                'position': 'after',
                'offset': 2
            }
        },
        'italic': {
            'desc': 'Mettre en italique',
            'syntaxe': '*texte*',
            'icon': 'fa-italic',
            'before': '*',
            'after': '*',
            'cursor': {
                'position': 'after',
                'offset': 1
            }
        },
        'image': {
            'desc': 'Insérer une image',
            'syntaxe': '![texte](http://)',
            'icon': 'fa-picture-o',
            'before': '![](',
            'after': ')',
            'cursor': {
                'position': 'before',
                'offset': 2
            }
        },
        'url': {
            'desc': 'Insérer un lien',
            'syntaxe': '[texte](http://), ou simplement <http://>',
            'icon': 'fa-link',
            'before': '[',
            'after': ']()',
            'cursor': {
                'position': 'after',
                'offset': 1
            }
        },
        'embed': {
            'desc': 'Intégrer un contenu',
            'syntaxe': '[!embed](http://)',
            'icon': 'fa-video-camera',
            'before': '[!embed](',
            'after': ')',
            'cursor': {
                'position': 'after',
                'offset': 1
            }
        },
        'quote': {
            'desc': 'Citation',
            'syntaxe': '> ligne',
            'icon': 'fa-comment',
            'before': '> ',
            'after': '',
            'cursor': {
                'position': 'after',
                'offset': 0
            }
        },
        'code': {
            'desc': 'Code',
            'syntaxe': '`code`, ou placer ``` sur les lignes adjacentes',
            'icon': 'fa-code',
            'before': '```\n',
            'after': '\n```',
            'cursor': {
                'position': 'after',
                'offset': 4
            }
        },
        'list': {
            'desc': 'Liste',
            'syntaxe': 'Préfixer la ligne par -',
            'icon': 'fa-list',
            'before': ' - ',
            'after': '',
            'cursor': {
                'position': 'after',
                'offset': 0
            }
        }
    }
};