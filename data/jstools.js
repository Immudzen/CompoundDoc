function select_option( selectbox, index )
{
    for( var i = 0; i < selectbox.options.length; i++ )
    {
        if( i == index )
            {
            selectbox.options[i].selected = true;
            }
        else
            {
            selectbox.options[i].selected = false;
            }
    }
}  
  
function jumpTo(self)
{
var value = self.value;
var location = new String(window.location);
var index = location.search("#");
if (index != -1)
    {
      var location = location.slice(0, index);
    }
var url = location + "#" + value;
select_option(self, 0);
window.location = url;
}

function loadRecord(self, elementSelector, sourceURL) {
var value = self.value;
$(""+elementSelector+"").load(""+sourceURL+value+"");
}