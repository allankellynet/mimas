
function enable_box(condition_id, target_id) {
 	if (document.getElementById(condition_id).value == "") {
 	    document.getElementById(target_id).value=""
		document.getElementById(target_id).disabled = true
	} else {
		document.getElementById(target_id).disabled = false
	}
}
