function dot2num(dot) {
           var d = dot.split('.');
           return ((((((+d[0]) * 256) + (+d[1])) * 256) + (+d[2])) * 256) + (+d[3]);
 }
 
function clean_subnet_size (ip) {
      ip = ip.replace(/\/[0-9][0-9]/, "");
      return ip;
}
      
$.fn.dataTableExt.oSort['string-ip-asc'] = function (x, y) {        
           x = clean_subnet_size(x);
           x = dot2num(x);
           y = clean_subnet_size(y);
           y = dot2num(y);
 
           return ((x < y) ? -1 : ((x > y) ? 1 : 0));
};
 
$.fn.dataTableExt.oSort['string-ip-desc'] = function (x, y) {
           x = clean_subnet_size(x);
           x = dot2num(x);
           y = clean_subnet_size(y);
           y = dot2num(y);
           return ((x < y) ? 1 : ((x > y) ? -1 : 0));
};