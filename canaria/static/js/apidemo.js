
function jsonRequestFailure(jqXHR, status, errorThrown){
    console.log(errorThrown);
}

function requestDataTable(target, dataSource){
    $.ajax({
        url: dataSource,
        type: 'GET',
        dataType: 'json',
        success: function(incoming) { insertDataTable(target, incoming); },
        error: jsonRequestFailure,
    });
}

function insertDataTable(target, data){
    console.log(target);
    console.log(data);
    data = data['data'];
    var columns = [];
    var rows = [];

    for(var key in data[0]){
        columns.push(key);
    }

    for(var i = 0; i < data.length; i++){
        var row = [];
        rows.push(row);
        for(var keyId in columns){
            row.push(data[i][columns[keyId]]);
        }
    }

	$(target)
		.TidyTable({
			columnTitles : columns,
			columnValues : rows,
		});
}
