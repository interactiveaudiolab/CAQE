/* Your custom JavaScript here */

/*
window.addEventListener('load', init, false);
function init() {
    try {

    }
    catch (e) {
        alert(e);
        window.location.href = "/sorry";
    }
}
*/


/*
This runs once the entire DOM has loaded.
*/

$(document).ready(function() {

    $('.instr').each(function(i) {
        $(this).prepend(i + '. ');
    });
});
