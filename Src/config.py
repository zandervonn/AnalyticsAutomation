shopify_defined_subheaders = [
	'order_number',
	'updated_at',
	'contact_email',
	'total_line_items_price',
	'discount_codes.code',
	'discount_codes.amount',
	'current_subtotal_price',
	'total_shipping_price_set.shop_money.amount',
	'total_tip_received',
	'current_total_price',
	'current_total_tax',
	'landing_site',
	'name',
	'note',
	'payment_gateway_names',
	'tags'
	# 'confirmation_number',
	# 'total_weight',
	# 'customer.id',
	# 'customer.email',
	# 'customer.first_name',
	# 'customer.last_name',
	# 'line_items.id',
	# 'line_items.name',
	# 'line_items.price',
	# 'fulfillments.id',
	# 'fulfillments.created_at',
]

starshipit_defined_subheaders = [
	'order_id',
	'order_date',
	'shipped_date',
	'order_number',
	# 'status',
	'order_type',
	'reference',
	'carrier',
	'carrier_name',
	'carrier_service_code',
	'shipping_method',
	# 'signature_required',
	# 'dangerous_goods',
	# 'currency',
	# 'sender_details.name',
	# 'sender_details.email',
	# 'sender_details.phone',
	# 'sender_details.street',
	# 'sender_details.suburb',
	# 'sender_details.city',
	# 'sender_details.state',
	# 'sender_details.post_code',
	# 'sender_details.country',
	# 'destination.name',
	# 'destination.email',
	# 'destination.street',
	# 'destination.suburb',
	# 'destination.city',
	# 'destination.state',
	'destination.post_code',
	'destination.country',
	# 'items.description',
	# 'items.sku',
	# 'items.country_of_origin',
	'items.quantity',
	'items.weight',
	# 'items.value',
	'packages.name',
	'packages.weight',
	# 'packages.height',
	# 'packages.width',
	# 'packages.length',
	'packages.packaging_type',
	# 'metadatas.metafield_key',
	# 'metadatas.value',
	'declared_value',
	# 'archived',
	# 'manifest_number',
	# 'address_validation',
	# 'create_return',
	# 'dtp',
	# 'add_insurance',
	# 'insurance_value',
	# 'plt',
	# 'type',
	# 'platform',

]