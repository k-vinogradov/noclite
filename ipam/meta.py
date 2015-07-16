import ipam.contrib

module_name = 'IPAM'
module_description = 'IP address management (IPAM) module for planning, tracking, and managing the Internet Protocol ' \
                     'address space used in a network.'
module_url_name = 'ipam.home'
module_icon = 'sitemap'
module_permissions = ['ipam.view', ]

search_func = ipam.contrib.search

