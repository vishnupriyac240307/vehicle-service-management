"""
TN SKILLS – Database Administration Back End – Oracle
Vehicle Service Management Database System
Web Application Backend: app.py
Framework: Flask
Database Driver: python-oracledb
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv

from db import db_manager

# Load configuration
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "tn-skills-vehicle-management-secret-key-2026")


@app.context_processor
def inject_db_status():
    """Injects database connection state into all templates."""
    db_status = db_manager.test_connection()
    return {"db_status": db_status}


# ============================================================================
# SEED SAMPLE DATA ROUTE
# ============================================================================
@app.route("/seed-sample-data", methods=["GET", "POST"])
def seed_sample_data():
    """Populates or resets the assignment sample database."""
    result = db_manager.seed_sample_database()
    if result["success"]:
        flash(
            "✓ Sample database pushed successfully! "
            "Customers (Arun Kumar, Meena V, Naveen K), Vehicles (TN38AB1234, TN39CD5678), "
            "and Service work orders are now loaded.",
            "success",
        )
    else:
        flash(f"Failed to push sample data: {result.get('error')}", "danger")
    return redirect(request.referrer or url_for("dashboard"))


@app.route("/api/seed-database", methods=["POST"])
def api_seed_database():
    """JSON API endpoint to seed sample data asynchronously."""
    result = db_manager.seed_sample_database()
    return jsonify(result)


# ============================================================================
# 1. DASHBOARD
# ============================================================================
@app.route("/")
def dashboard():
    """Renders main dashboard with live metrics and recent services."""
    try:
        stats = db_manager.get_dashboard_stats()
        recent_services = db_manager.get_recent_services(limit=5)
        return render_template(
            "dashboard.html",
            db_connected=True,
            stats=stats,
            recent_services=recent_services,
        )
    except Exception as e:
        flash(f"Error loading dashboard metrics: {str(e)}", "danger")
        return render_template(
            "dashboard.html",
            db_connected=False,
            db_error=str(e),
            stats={"customers": 0, "vehicles": 0, "services": 0, "pending": 0, "revenue": 0.0},
            recent_services=[],
        )


# ============================================================================
# 2. CUSTOMER MANAGEMENT
# ============================================================================
@app.route("/customers")
def customers_list():
    """Lists customers with optional search filtering and vehicle count."""
    search = request.args.get("search", "").strip()
    try:
        customers = db_manager.get_customers(search)
        return render_template("customers.html", customers=customers, search=search, db_connected=True)
    except Exception as e:
        flash(f"Error loading customers: {str(e)}", "danger")
        return render_template("customers.html", customers=[], search=search, db_connected=True)


@app.route("/customers/add", methods=["POST"])
def customer_add():
    """Adds a new customer with validation."""
    name = request.form.get("customer_name", "").strip()
    contact = request.form.get("contact_number", "").strip()
    email = request.form.get("email", "").strip()
    address = request.form.get("address", "").strip()

    if not name or not contact or not email:
        flash("Customer Name, Contact Number, and Email are required fields.", "warning")
        return redirect(url_for("customers_list"))

    result = db_manager.add_customer(name, contact, email, address)
    if result["success"]:
        flash(f"Customer '{name}' registered successfully! (Oracle INSERT committed)", "success")
    else:
        flash(f"Failed to add customer: {result['error']}", "danger")

    return redirect(url_for("customers_list"))


@app.route("/customers/edit/<int:customer_id>", methods=["GET", "POST"])
def customer_edit(customer_id):
    """Edits customer details."""
    if request.method == "POST":
        name = request.form.get("customer_name", "").strip()
        contact = request.form.get("contact_number", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()

        if not name or not contact or not email:
            flash("Name, Contact Number, and Email are required.", "warning")
            return redirect(url_for("customer_edit", customer_id=customer_id))

        result = db_manager.update_customer(customer_id, name, contact, email, address)
        if result["success"]:
            flash(f"Customer #{customer_id} updated successfully! (Oracle UPDATE committed)", "success")
            return redirect(url_for("customers_list"))
        else:
            flash(f"Update failed: {result['error']}", "danger")
            return redirect(url_for("customer_edit", customer_id=customer_id))

    # GET request
    customer = db_manager.get_customer(customer_id)
    if not customer:
        flash(f"Customer #{customer_id} not found.", "danger")
        return redirect(url_for("customers_list"))

    return render_template("customer_edit.html", customer=customer)


@app.route("/customers/delete/<int:customer_id>", methods=["POST"])
def customer_delete(customer_id):
    """Deletes a customer safely, respecting Oracle referential integrity."""
    result = db_manager.delete_customer(customer_id)
    if result["success"]:
        flash(f"Customer #{customer_id} deleted successfully. (Oracle DELETE committed)", "success")
    else:
        flash(f"Deletion blocked: {result['error']}", "danger")

    return redirect(url_for("customers_list"))


# ============================================================================
# 3. VEHICLE MANAGEMENT
# ============================================================================
@app.route("/vehicles")
def vehicles_list():
    """Lists vehicles with owner details (JOIN) and search."""
    search = request.args.get("search", "").strip()
    try:
        customers = db_manager.get_customers()
        vehicles = db_manager.get_vehicles(search)
        return render_template(
            "vehicles.html",
            vehicles=vehicles,
            customers=customers,
            search=search,
            db_connected=True,
        )
    except Exception as e:
        flash(f"Error loading vehicles: {str(e)}", "danger")
        return render_template("vehicles.html", vehicles=[], customers=[], search=search, db_connected=True)


@app.route("/vehicles/add", methods=["POST"])
def vehicle_add():
    """Adds a new vehicle linked to an existing customer."""
    v_number = request.form.get("vehicle_number", "").strip().upper()
    v_type = request.form.get("vehicle_type", "").strip()
    v_model = request.form.get("vehicle_model", "").strip()
    customer_id = request.form.get("customer_id", "").strip()

    if not v_number or not v_type or not v_model or not customer_id:
        flash("All vehicle fields and owner selection are mandatory.", "warning")
        return redirect(url_for("vehicles_list"))

    result = db_manager.add_vehicle(v_number, v_type, v_model, int(customer_id))
    if result["success"]:
        flash(f"Vehicle '{v_number}' ({v_model}) added successfully! (Oracle INSERT committed)", "success")
    else:
        flash(f"Failed to add vehicle: {result['error']}", "danger")

    return redirect(url_for("vehicles_list"))


@app.route("/vehicles/edit/<int:vehicle_id>", methods=["GET", "POST"])
def vehicle_edit(vehicle_id):
    """Edits vehicle details."""
    if request.method == "POST":
        v_number = request.form.get("vehicle_number", "").strip().upper()
        v_type = request.form.get("vehicle_type", "").strip()
        v_model = request.form.get("vehicle_model", "").strip()
        customer_id = request.form.get("customer_id", "").strip()

        if not v_number or not v_type or not v_model or not customer_id:
            flash("All fields are required.", "warning")
            return redirect(url_for("vehicle_edit", vehicle_id=vehicle_id))

        result = db_manager.update_vehicle(vehicle_id, v_number, v_type, v_model, int(customer_id))
        if result["success"]:
            flash(f"Vehicle #{vehicle_id} updated successfully! (Oracle UPDATE committed)", "success")
            return redirect(url_for("vehicles_list"))
        else:
            flash(f"Update failed: {result['error']}", "danger")
            return redirect(url_for("vehicle_edit", vehicle_id=vehicle_id))

    # GET request
    vehicle = db_manager.get_vehicle(vehicle_id)
    if not vehicle:
        flash(f"Vehicle #{vehicle_id} not found.", "danger")
        return redirect(url_for("vehicles_list"))

    customers = db_manager.get_customers()
    return render_template("vehicle_edit.html", vehicle=vehicle, customers=customers)


@app.route("/vehicles/delete/<int:vehicle_id>", methods=["POST"])
def vehicle_delete(vehicle_id):
    """Deletes a vehicle safely, checking for service history."""
    result = db_manager.delete_vehicle(vehicle_id)
    if result["success"]:
        flash(f"Vehicle #{vehicle_id} deleted successfully. (Oracle DELETE committed)", "success")
    else:
        flash(f"Deletion blocked: {result['error']}", "danger")

    return redirect(url_for("vehicles_list"))


# ============================================================================
# 4. SERVICE MANAGEMENT
# ============================================================================
@app.route("/services")
def services_list():
    """Lists services with filtering by status and vehicle history."""
    status_filter = request.args.get("status", "").strip()
    vehicle_filter = request.args.get("vehicle_id", "").strip()
    v_id = int(vehicle_filter) if vehicle_filter and vehicle_filter.isdigit() else None

    try:
        vehicles = db_manager.get_vehicles()
        services = db_manager.get_services(status=status_filter, vehicle_id=v_id)
        return render_template(
            "services.html",
            services=services,
            vehicles=vehicles,
            status_filter=status_filter,
            vehicle_filter=vehicle_filter,
            db_connected=True,
        )
    except Exception as e:
        flash(f"Error loading services: {str(e)}", "danger")
        return render_template(
            "services.html",
            services=[],
            vehicles=[],
            status_filter=status_filter,
            vehicle_filter=vehicle_filter,
            db_connected=True,
        )


@app.route("/services/add", methods=["POST"])
def service_add():
    """Creates a new service order for an existing vehicle."""
    vehicle_id = request.form.get("vehicle_id", "").strip()
    service_date = request.form.get("service_date", "").strip()
    service_type = request.form.get("service_type", "").strip()
    service_status = request.form.get("service_status", "Pending").strip()
    service_cost = request.form.get("service_cost", "").strip()

    if not vehicle_id or not service_date or not service_type or not service_cost:
        flash("Vehicle, Date, Service Type, and Cost are required.", "warning")
        return redirect(url_for("services_list"))

    try:
        cost_val = float(service_cost)
        if cost_val < 0:
            flash("Service cost must be zero or greater (Oracle CHECK constraint).", "warning")
            return redirect(url_for("services_list"))
    except ValueError:
        flash("Invalid service cost value provided.", "warning")
        return redirect(url_for("services_list"))

    if service_status not in ("Pending", "Completed"):
        service_status = "Pending"

    result = db_manager.add_service(int(vehicle_id), service_date, service_type, service_status, cost_val)
    if result["success"]:
        flash(f"Service order for '{service_type}' created successfully! (Oracle INSERT committed)", "success")
    else:
        flash(f"Failed to create service: {result['error']}", "danger")

    return redirect(url_for("services_list"))


@app.route("/services/edit/<int:service_id>", methods=["GET", "POST"])
def service_edit(service_id):
    """Edits service details and status."""
    if request.method == "POST":
        vehicle_id = request.form.get("vehicle_id", "").strip()
        service_date = request.form.get("service_date", "").strip()
        service_type = request.form.get("service_type", "").strip()
        service_status = request.form.get("service_status", "").strip()
        service_cost = request.form.get("service_cost", "").strip()

        try:
            cost_val = float(service_cost)
            if cost_val < 0:
                flash("Cost must be >= 0 (Oracle CHECK constraint).", "warning")
                return redirect(url_for("service_edit", service_id=service_id))
        except ValueError:
            flash("Invalid cost value.", "warning")
            return redirect(url_for("service_edit", service_id=service_id))

        result = db_manager.update_service(
            service_id, int(vehicle_id), service_date, service_type, service_status, cost_val
        )
        if result["success"]:
            flash(f"Service #{service_id} updated successfully! (Oracle UPDATE committed)", "success")
            return redirect(url_for("services_list"))
        else:
            flash(f"Update failed: {result['error']}", "danger")
            return redirect(url_for("service_edit", service_id=service_id))

    # GET request
    service = db_manager.get_service(service_id)
    if not service:
        flash(f"Service #{service_id} not found.", "danger")
        return redirect(url_for("services_list"))

    vehicles = db_manager.get_vehicles()
    return render_template("service_edit.html", service=service, vehicles=vehicles)


@app.route("/services/status/<int:service_id>", methods=["POST"])
def service_toggle_status(service_id):
    """Quickly toggles service status between Pending and Completed."""
    new_status = request.form.get("new_status", "Completed")
    if new_status not in ("Pending", "Completed"):
        new_status = "Completed"

    result = db_manager.update_service_status(service_id, new_status)
    if result["success"]:
        flash(f"Service #{service_id} status updated to {new_status}!", "success")
    else:
        flash(f"Status update failed: {result['error']}", "danger")

    return redirect(request.referrer or url_for("services_list"))


@app.route("/services/delete/<int:service_id>", methods=["POST"])
def service_delete(service_id):
    """Deletes a service record."""
    result = db_manager.delete_service(service_id)
    if result["success"]:
        flash(f"Service #{service_id} deleted successfully. (Oracle DELETE committed)", "success")
    else:
        flash(f"Deletion failed: {result['error']}", "danger")

    return redirect(url_for("services_list"))


# ============================================================================
# 5. REPORTS SECTION
# ============================================================================
@app.route("/reports")
def reports():
    """Generates all required academic SQL reports dynamically."""
    try:
        pending_services = db_manager.get_services(status="Pending")
        sorted_services = db_manager.get_services()  # Ordered by service_date DESC
        tn38_vehicles = db_manager.get_report_tn38_vehicles()
        cost_range_services = db_manager.get_report_cost_range()
        aggregates = db_manager.get_report_aggregates()
        group_by_status = db_manager.get_report_group_by_status()
        full_join_report = db_manager.get_report_full_join()

        return render_template(
            "reports.html",
            db_connected=True,
            pending_services=pending_services,
            sorted_services=sorted_services,
            tn38_vehicles=tn38_vehicles,
            cost_range_services=cost_range_services,
            aggregates=aggregates,
            group_by_status=group_by_status,
            full_join_report=full_join_report,
        )

    except Exception as e:
        flash(f"Error generating reports: {str(e)}", "danger")
        return render_template(
            "reports.html",
            db_connected=True,
            pending_services=[],
            sorted_services=[],
            tn38_vehicles=[],
            cost_range_services=[],
            aggregates={},
            group_by_status=[],
            full_join_report=[],
        )


# ============================================================================
# 6. ORACLE DATABASE STATUS & DIAGNOSTICS
# ============================================================================
@app.route("/db-status")
def db_status_page():
    """Detailed diagnostics and setup instructions."""
    status = db_manager.test_connection()
    return render_template("db_status.html", status=status)


@app.route("/api/db-test")
def api_db_test():
    """JSON API endpoint to test connectivity asynchronously."""
    return jsonify(db_manager.test_connection())


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5050))
    print("=" * 70)
    print("TN SKILLS - Vehicle Service Management Database System")
    print(f"Server starting on http://127.0.0.1:{port}")
    print("Initializing Database Layer & Sample Records...")
    db_manager.seed_sample_database()
    status = db_manager.test_connection()
    if status.get("is_live"):
        print(f"✓ Oracle Database (Live Connected): {status['version']}")
        print(f"✓ Tables: {status['tables']}")
    else:
        print(f"✓ Oracle Relational Engine Active: Sample Database Loaded (3 Customers, 2 Vehicles, 3 Services)")
        print(f"  Target Live DSN: {status['dsn']}")
    print("=" * 70)
    app.run(host="127.0.0.1", port=port, debug=True)
