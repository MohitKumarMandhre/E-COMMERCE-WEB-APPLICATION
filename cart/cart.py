from decimal import Decimal
from django.conf import settings
from shop.models import Product

# This	is	the	Cart	class	that	will	allow	us	to	manage	the	shopping	cart.
# We	require	the	cart	to	be	initialized	with	a	request	object.	We	store
# the	current	session	using	self.session	=	request.session	to	make	it
# accessible	to	the	other	methods	of	the	Cart	class.	First,	we	try	to	get
# the	cart	from	the	current	session	using
# self.session.get(settings.CART_SESSION_ID).	If	no	cart	is	present	in	the
# session,	we	create	an	empty	cart	by	setting	an	empty	dictionary	in
# the	session.	We	expect	our	cart	dictionary	to	use	product	IDs	as
# keys	and	a	dictionary	with	quantity	and	price	as	the	value	for	each
# key.	By	doing	so,	we	can	guarantee	that	a	product	is	not	added	more
# than	once	in	the	cart;	this	way	we	also	simplify	the	way	to	retrieve
# cart	items

class Cart(object):

    def __init__(self, request):

        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        # Add	a	product	to	the	cart	or	update	its	quantity.
        product_id = str(product.id)
        # beacuse django only allows str in json

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity' : 0,
                'price' : str(product.price),
            }
        if update_quantity :
            self.cart[product_id]['quantity'] =	quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        #	mark	the	session	as	"modified"	to	make	sure	it	gets	saved
        self.session.modified = True

    def remove(self, product):
        # Remove	a	product	from	the	cart.
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        # Iterate	over	the	items	in	the	cart	and	get	the	products	
		# 						from	the	database.
        product_ids = self.cart.keys()
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in = product_ids)

        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def	__len__(self):
        return	sum(item['quantity'] for item in self.cart.values())

    def	get_total_price(self):
        return sum( Decimal(item['price']) * item['quantity'] for item in self.cart.values() )

    def	clear(self):
        #	remove	cart	from	session
        del	self.session[settings.CART_SESSION_ID]
        self.save()