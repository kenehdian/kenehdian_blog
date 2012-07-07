//This code is quite embarrasing but it does what I need it to do for now.
//In the future, get rid of this junk and write some unobtrusive jQuery.
function applyTag(obj, tag, styleClass) {
    if (styleClass != "") {
        wrapText(obj, '<' + tag + ' class="' + styleClass + '">', '</' + tag + '>');
    }
    else {
        wrapText(obj, '<' + tag + '>', '</' + tag + '>');
    }
};

function wrapText(obj, beginTag, endTag) {
    if (typeof obj.selectionStart == 'number') {
        // Mozilla, Opera, and other browsers
        var start = obj.selectionStart;
        var end = obj.selectionEnd;

        obj.value = obj.value.substring(0, start) + beginTag + obj.value.substring(start, end) + endTag + obj.value.substring(end, obj.value.length);
    }
    else if (document.selection) {
        obj.focus();
        var range = document.selection.createRange();
        if (range.parentElement() != obj) return false;

        if (typeof range.text == 'string')
            document.selection.createRange().text = beginTag + range.text + endTag;
    }
    else
        obj.value += text;

};