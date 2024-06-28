from bitpay import Client

bitpay = Client.create_pos_client('somePosToken', Environment.TEST)


invoice = Invoice()
invoice.full_notifications = True
invoice.extended_notifications = True
invoice.notification_url = "https://test/lJnJg9WW7MtG9GZlPVdj"
invoice.redirect_url = "https://test/lJnJg9WW7MtG9GZlPVdj"
invoice.notification_email = "my@email.com"

buyer = Buyer()
buyer.name = "Test"
buyer.email = "test@email.com"
buyer.address1 = "168 General Grove"
buyer.country = "AD"
buyer.locality = "Port Horizon"
buyer.notify = True
buyer.phone = "+990123456789"
buyer.postal_code = "KY7 1TH"
buyer.region = "New Port"

invoice.buyer = buyer

result = bitpay.create_invoice(invoice, Facade.POS, False)