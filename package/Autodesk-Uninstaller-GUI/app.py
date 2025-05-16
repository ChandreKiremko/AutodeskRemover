import os
import logging
from flask import Flask, render_template, jsonify, request, session
from utils.ps_scripts import (
    check_admin_rights,
    get_installed_autodesk_products,
    uninstall_products,
    delete_autodesk_folder,
    restart_computer
)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "autodesk-uninstaller-secret")

@app.route('/')
def index():
    """Main page route"""
    is_admin = check_admin_rights()
    
    if not is_admin:
        logger.warning("Application not running with admin rights")
        return render_template('index.html', error="This application requires administrator privileges to function properly.")
    
    try:
        installed_products = get_installed_autodesk_products()
        return render_template('index.html', products=installed_products, is_admin=is_admin)
    except Exception as e:
        logger.error(f"Error retrieving installed products: {str(e)}")
        return render_template('index.html', 
                              error=f"Error retrieving installed products: {str(e)}",
                              is_admin=is_admin)

@app.route('/get-products', methods=['GET'])
def get_products():
    """API endpoint to get all installed Autodesk products"""
    try:
        products = get_installed_autodesk_products()
        return jsonify({'success': True, 'products': products})
    except Exception as e:
        logger.error(f"Error retrieving installed products: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/uninstall', methods=['POST'])
def uninstall():
    """API endpoint to uninstall selected products"""
    try:
        data = request.json
        product_ids = data.get('productIds', [])
        delete_folder = data.get('deleteFolder', False)
        restart_pc = data.get('restartComputer', False)
        
        if not product_ids:
            return jsonify({'success': False, 'error': 'No products selected for uninstallation'})
        
        logger.info(f"Starting uninstallation of {len(product_ids)} products")
        
        # Store uninstallation session data
        session['uninstall_in_progress'] = True
        session['products_to_uninstall'] = product_ids
        
        # Start the uninstallation process
        uninstall_results = uninstall_products(product_ids)
        
        # Handle additional requested operations
        autodesk_folder_deleted = False
        if delete_folder:
            autodesk_folder_deleted = delete_autodesk_folder()
        
        # After successful uninstallation and folder deletion, restart if requested
        if restart_pc:
            restart_computer()
            return jsonify({'success': True, 'message': 'Uninstallation complete. System is restarting...'})
        
        return jsonify({
            'success': True, 
            'message': 'Uninstallation completed successfully',
            'results': uninstall_results,
            'folderDeleted': autodesk_folder_deleted
        })
        
    except Exception as e:
        logger.error(f"Error during uninstallation: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})
    finally:
        # Clear uninstallation session data
        session.pop('uninstall_in_progress', None)
        session.pop('products_to_uninstall', None)

@app.route('/uninstall-status', methods=['GET'])
def uninstall_status():
    """API endpoint to check uninstallation status"""
    in_progress = session.get('uninstall_in_progress', False)
    products = session.get('products_to_uninstall', [])
    
    return jsonify({
        'inProgress': in_progress,
        'products': products
    })
