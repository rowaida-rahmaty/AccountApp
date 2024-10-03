from flask import Blueprint , render_template, request, redirect, url_for, flash,session, jsonify
from flask_login import login_required, current_user
from .models import Product,InventoryTransaction
from app import db
from .form import ProductForm, ProductEditForm, RecordPurchaseForm, RecordSaleForm
from flask import request, jsonify, session, flash
import csv
from io import StringIO
from flask import Response


views = Blueprint('views', __name__)
@views.route('/')
@views.route('/home')
@login_required
def home():
    return render_template('home.html')


@views.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    form = ProductForm()

    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        cost = form.cost.data
        price = form.price.data
        quantity = form.quantity.data
        reorder_level = form.reorder_level.data

        # Check if product already exists
        existing_product = Product.query.filter_by(name=name, description=description).first()
        
        if existing_product:
            flash('Product already exists!', 'danger')
        else:
            new_product = Product(
                name=name,
                description=description,
                cost = cost,
                price=price,
                quantity=quantity,
                reorder_level=reorder_level,
                user_id=current_user.id  # Get the current logged-in user's ID
            )
            db.session.add(new_product)
            db.session.commit()
        
            flash('Product added successfully!', 'success')

        return redirect(url_for('views.product_list'))  # Redirect to product list page
    
    return render_template('products.html', form=form)



@views.route('/product_list')
@login_required
def product_list():
    products = Product.get_all_products(user_id=current_user.id)
    return render_template('product_list.html', products=products)




@views.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    #user_id = session.get('user_id')
    
    if not current_user:
        flash("You need to be logged in to edit a product.")
        return redirect(url_for('auth.login'))
    
    product = Product.query.get_or_404(product_id)
    
    form = ProductEditForm(obj=product)
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.cost = form.cost.data
        product.price = form.price.data
        product.quantity = form.quantity.data
        product.reorder_level = form.reorder_level.data
        
        db.session.commit()
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('views.product_list'))
    
    return render_template('edit_product.html', form=form, product=product)


@views.route('/record_sale', methods=['GET', 'POST'])
@login_required
def record_sale():
    form = RecordSaleForm()
    products = Product.get_all_products(user_id=current_user.id)
    form.product_id.choices = [(p.id, p.name) for p in products]

    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)
        if product and product.quantity >= form.quantity.data:
            # Create a transaction record
            transaction = InventoryTransaction(
                product_id=product.id,
                quantity_changed=form.quantity.data,
                transaction_type="OUT"
            )
            transaction.record()
            
            flash('Sale recorded successfully!', 'success')
            return redirect(url_for('views.product_list'))
        flash('Product not found or insufficient quantity.', 'danger')

    return render_template('record_sale.html', form=form)


@views.route('/record_purchase', methods=['GET', 'POST'])
@login_required
def record_purchase():
    form = RecordPurchaseForm()
    products = Product.get_all_products(user_id=current_user.id)
    form.product_id.choices = [(p.id, p.name) for p in products]

    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)
        if product:
            # Create a transaction record
            transaction = InventoryTransaction(
                product_id=product.id,
                quantity_changed=form.quantity.data,
                transaction_type="IN"
            )
            transaction.record()
            
            flash('Purchase recorded successfully!', 'success')
            return redirect(url_for('views.product_list'))
        flash('Product not found.', 'danger')

    return render_template('record_purchase.html', form=form)



@views.route('/delete_flash_message', methods=['POST'])
@login_required
def delete_flash_message():
    data = request.get_json()
    message_id = data.get("message_id")

    # Retrieve flashed messages stored in the session
    messages = session.get('_flashes', [])

    # Remove the message if it exists
    if message_id and 0 <= message_id - 1 < len(messages):
        del messages[message_id - 1]
        session['_flashes'] = messages  # Update session with the modified messages

    return jsonify({"success": True})


@views.route('/product_history', methods=['GET'])
@login_required
def product_history():
    products = Product.query.filter_by(user_id=current_user.id).all()

    product_summaries = []
    total_revenue_all = 0
    total_cogs_all = 0
    total_inventory_cost_all = 0
    total_cash_outflows_all = 0  # New variable to track total cash outflows

    for product in products:
        transactions = InventoryTransaction.query.filter_by(product_id=product.id).order_by(InventoryTransaction.date.asc()).all()

        total_revenue = 0
        total_cogs = 0
        total_sold = 0
        total_purchased = 0
        total_cash_outflows = 0  # Track cash outflows for this product

        for t in transactions:
            if t.transaction_type == "OUT":
                # Calculate revenue from sales
                revenue = t.quantity_changed * product.price
                cogs = t.quantity_changed * product.cost
                total_revenue += revenue
                total_cogs += cogs
                total_sold += t.quantity_changed

            elif t.transaction_type == "IN":
                # Track purchases and cash outflows
                total_purchased += t.quantity_changed
                cash_outflow = t.quantity_changed * product.cost  # Calculate cost of purchase
                total_cash_outflows += cash_outflow  # Add purchase to total cash outflows for this product
                print(f"Adding {t.quantity_changed} to total_purchased for product {product.name}")

        # Calculate current inventory cost
        inventory_cost = product.quantity * product.cost

        # Calculate profit
        total_profit = total_revenue - total_cogs

        # Update overall totals
        total_revenue_all += total_revenue
        total_cogs_all += total_cogs
        total_inventory_cost_all += inventory_cost
        total_cash_outflows_all += total_cash_outflows  # Add product's cash outflows to overall total

        product_summaries.append({
            'product': product,
            'total_revenue': total_revenue,
            'total_profit': total_profit,
            'total_cogs': total_cogs,
            'total_sold': total_sold,
            'inventory_cost': inventory_cost,
            'total_purchased': total_purchased,
            'total_cash_outflows': total_cash_outflows,  # Add cash outflows to summary
        })

    # Total cash inflows are the total revenue
    total_cash_movement = total_revenue_all - total_cash_outflows_all  # Calculate total cash movement

    return render_template(
        'product_history.html', 
        product_summaries=product_summaries,
        total_cash_outflows_all=total_cash_outflows_all,  # Pass total cash outflows to the template
        total_revenue_all=total_revenue_all,
        total_cogs_all=total_cogs_all,
        total_inventory_cost_all=total_inventory_cost_all,
        total_profit_all=total_revenue_all - total_cogs_all,  # Gross profit
        total_cash_movement=total_cash_movement,  # Pass total cash movement to the template
    )




@views.route('/product_transaction_history/<int:product_id>', methods=['GET'])
@login_required
def product_transaction_history(product_id):
    product = Product.query.filter_by(id=product_id, user_id=current_user.id).first_or_404()
    transactions = InventoryTransaction.query.filter_by(product_id=product_id).order_by(InventoryTransaction.date.asc()).all()

    return render_template(
        'product_transaction_history.html',
        product=product,
        transactions=transactions
    )

@views.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.filter_by(id=product_id, user_id=current_user.id).first_or_404()
    
    # Optionally, you may want to check if there are any transactions associated with the product.
    # If there are, you might need to handle them before deletion.

    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('views.product_list'))



@views.route('/download_product_history')
@login_required
def download_product_history():
    products = Product.query.filter_by(user_id=current_user.id).all()
    
    # Create a CSV in-memory file
    output = StringIO()
    writer = csv.writer(output)
    
    # Write CSV header
    writer.writerow([
        'Product Name', 'Cost per Unit', 'Sale Price per Unit', 'Purchases (Units)', 
        'Products Sold (Units)', 'Cost of Goods Sold (COGS)', 'Total Revenue', 'Profit/Loss'
    ])
    
    for product in products:
        transactions = InventoryTransaction.query.filter_by(product_id=product.id).order_by(InventoryTransaction.date.asc()).all()
        
        total_cost = 0
        total_revenue = 0
        total_profit = 0
        total_cogs = 0
        total_purchases = 0
        total_sold = 0

        for transaction in transactions:
            if transaction.transaction_type == 'OUT':  # Sale
                revenue = transaction.quantity_changed * product.price
                cogs = transaction.quantity_changed * product.cost
                total_revenue += revenue
                total_cogs += cogs
                total_sold += transaction.quantity_changed
            elif transaction.transaction_type == 'IN':  # Purchase
                cost = transaction.quantity_changed * product.cost
                total_cost += cost
                total_purchases += transaction.quantity_changed

        total_profit = total_revenue - total_cogs
        
        writer.writerow([
            product.name, product.cost, product.price, total_purchases, total_sold,
            total_cogs, total_revenue, total_profit
        ])
    
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=product_history.csv"}
    )



@views.route('/download_product_transactions/<int:product_id>')
@login_required
def download_product_transactions(product_id):
    product = Product.query.filter_by(id=product_id, user_id=current_user.id).first_or_404()
    transactions = InventoryTransaction.query.filter_by(product_id=product_id).order_by(InventoryTransaction.date.asc()).all()
    
    # Create a CSV in-memory file
    output = StringIO()
    writer = csv.writer(output)
    
    # Write CSV header
    writer.writerow([
        'Date', 'Type', 'Quantity', 'Unit Cost', 'Sale Price', 'Total Cost', 'Total Sale', 'Total Profit/Loss'
    ])
    
    for transaction in transactions:
        if transaction.transaction_type == 'IN':
            unit_cost = product.cost
            sale_price = 'N/A'
            total_cost = transaction.quantity_changed * product.cost
            total_sale = 'N/A'
            total_profit_loss = 'N/A'
        elif transaction.transaction_type == 'OUT':
            unit_cost = 'N/A'
            sale_price = product.price
            total_cost = 'N/A'
            total_sale = transaction.quantity_changed * product.price
            total_profit_loss = total_sale - (transaction.quantity_changed * product.cost)
        else:
            unit_cost = sale_price = total_cost = total_sale = total_profit_loss = 'N/A'
        
        writer.writerow([
            transaction.date.strftime('%Y-%m-%d %H:%M:%S'),
            transaction.transaction_type,
            transaction.quantity_changed,
            unit_cost,
            sale_price,
            total_cost,
            total_sale,
            total_profit_loss
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=product_{product_id}_transactions.csv"}
    )
