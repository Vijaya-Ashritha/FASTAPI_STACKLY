vehicles = []
rentals = []


# ADD VEHICLE 

def add_vehicle():
    try:
        vehicle_id = input("Enter Vehicle ID: ").strip()

        if not vehicle_id:
            raise ValueError("Vehicle ID cannot be empty.")

        # Check duplicate Vehicle ID
        for vehicle in vehicles:
            if vehicle["vehicle_id"] == vehicle_id:
                raise ValueError("Duplicate Vehicle ID.")

        vehicle_name = input("Enter Vehicle Name: ").strip()

        if not vehicle_name:
            raise ValueError("Vehicle Name cannot be empty.")

        vehicle_type = input("Enter Vehicle Type (Bike/Car/SUV): ").strip().title()

        if vehicle_type not in ["Bike", "Car", "SUV"]:
            raise ValueError("Invalid Vehicle Type. Choose Bike, Car, or SUV.")

        price = float(input("Enter Rental Price Per Day: "))

        if price <= 0:
            raise ValueError("Vehicle price must be greater than 0.")

        vehicle = {
            "vehicle_id": vehicle_id,
            "vehicle_name": vehicle_name,
            "vehicle_type": vehicle_type,
            "price_per_day": price,
            "available": True
        }

        vehicles.append(vehicle)

        print("Vehicle added successfully.")

    except ValueError as error:
        print("Error:", error)


# VIEW AVAILABLE VEHICLES

def view_available_vehicles():
    print("\n__AVAILABLE VEHICLES__")

    found = False

    for vehicle in vehicles:
        if vehicle["available"]:
            found = True

            print(
                f"ID: {vehicle['vehicle_id']} | "
                f"Name: {vehicle['vehicle_name']} | "
                f"Type: {vehicle['vehicle_type']} | "
                f"Price/Day: ₹{vehicle['price_per_day']:.2f}"
            )

    if not found:
        print("No vehicles are currently available.")


# RENT VEHICLE 

def rent_vehicle():
    try:
        customer_id = input("Enter Customer ID: ").strip()

        if not customer_id:
            raise ValueError("Customer ID cannot be empty.")

        # Customer ID must be unique for active rentals
        for rental in rentals:
            if (
                rental["customer_id"] == customer_id
                and not rental["returned"]
            ):
                raise ValueError(
                    "Customer ID already has an active rental."
                )

        customer_name = input("Enter Customer Name: ").strip()

        if not customer_name:
            raise ValueError("Customer name cannot be empty.")

        vehicle_id = input("Enter Vehicle ID: ").strip()

        if not vehicle_id:
            raise ValueError("Vehicle ID cannot be empty.")

        # Find vehicle
        selected_vehicle = None

        for vehicle in vehicles:
            if vehicle["vehicle_id"] == vehicle_id:
                selected_vehicle = vehicle
                break

        if selected_vehicle is None:
            raise ValueError("Invalid Vehicle ID.")

        # Check availability
        if not selected_vehicle["available"]:
            raise ValueError("Vehicle is not available.")

        rental_days = int(input("Enter Number of Rental Days: "))

        if rental_days <= 0:
            raise ValueError("Rental days must be greater than 0.")

        # Calculate rental amount
        price_per_day = selected_vehicle["price_per_day"]

        total_amount = price_per_day * rental_days

        discount = 0

        # 10% discount for 7 or more days
        if rental_days >= 7:
            discount = total_amount * 0.10

        final_amount = total_amount - discount

        # Create rental record
        rental = {
            "customer_id": customer_id,
            "customer_name": customer_name,
            "vehicle_id": vehicle_id,
            "vehicle_name": selected_vehicle["vehicle_name"],
            "rental_days": rental_days,
            "price_per_day": price_per_day,
            "total_amount": total_amount,
            "discount": discount,
            "final_amount": final_amount,
            "returned": False
        }

        rentals.append(rental)

        # Make vehicle unavailable
        selected_vehicle["available"] = False

        print("\nVehicle rented successfully.")
        print(f"Total Amount: ₹{total_amount:.2f}")
        print(f"Discount: ₹{discount:.2f}")
        print(f"Final Amount: ₹{final_amount:.2f}")

    except ValueError as error:
        print("Error:", error)


# RETURN VEHICLE 

def return_vehicle():
    try:
        vehicle_id = input("Enter Vehicle ID to return: ").strip()

        if not vehicle_id:
            raise ValueError("Vehicle ID cannot be empty.")

        # Find active rental
        active_rental = None

        for rental in rentals:
            if (
                rental["vehicle_id"] == vehicle_id
                and not rental["returned"]
            ):
                active_rental = rental
                break

        if active_rental is None:
            raise ValueError("Invalid Vehicle ID or vehicle is not rented.")

        # Mark rental as returned
        active_rental["returned"] = True

        # Make vehicle available again
        for vehicle in vehicles:
            if vehicle["vehicle_id"] == vehicle_id:
                vehicle["available"] = True
                break

        print("Vehicle returned successfully.")

    except ValueError as error:
        print("Error:", error)


# SEARCH RENTAL BY CUSTOMER ID 

def search_rental():
    try:
        customer_id = input("Enter Customer ID: ").strip()

        if not customer_id:
            raise ValueError("Customer ID cannot be empty.")

        found = False

        for rental in rentals:
            if rental["customer_id"] == customer_id:
                found = True

                print("\n--- RENTAL DETAILS ---")
                print("Customer ID:", rental["customer_id"])
                print("Customer Name:", rental["customer_name"])
                print("Vehicle ID:", rental["vehicle_id"])
                print("Vehicle Name:", rental["vehicle_name"])
                print("Rental Days:", rental["rental_days"])
                print(
                    "Price Per Day:",
                    f"₹{rental['price_per_day']:.2f}"
                )
                print(
                    "Total Amount:",
                    f"₹{rental['total_amount']:.2f}"
                )
                print(
                    "Discount:",
                    f"₹{rental['discount']:.2f}"
                )
                print(
                    "Final Amount:",
                    f"₹{rental['final_amount']:.2f}"
                )

                if rental["returned"]:
                    print("Status: Returned")
                else:
                    print("Status: Active")

        if not found:
            raise ValueError("Invalid Customer ID.")

    except ValueError as error:
        print("Error:", error)


# DISPLAY ALL RENTED VEHICLES 
def display_rented_vehicles():
    print("\n__RENTED VEHICLES__")

    found = False

    for rental in rentals:
        if not rental["returned"]:
            found = True

            print(
                f"Customer: {rental['customer_name']} | "
                f"Customer ID: {rental['customer_id']} | "
                f"Vehicle: {rental['vehicle_name']} | "
                f"Vehicle ID: {rental['vehicle_id']} | "
                f"Days: {rental['rental_days']} | "
                f"Amount: ₹{rental['final_amount']:.2f}"
            )

    if not found:
        print("No vehicles are currently rented.")


# RENTAL SUMMARY REPORT 

def rental_summary_report():
    print("\n___RENTAL SUMMARY REPORT___")

    total_rentals = len(rentals)

    active_rentals = 0
    returned_rentals = 0
    total_revenue = 0
    total_discount = 0

    for rental in rentals:
        if rental["returned"]:
            returned_rentals += 1
        else:
            active_rentals += 1

        total_revenue += rental["final_amount"]
        total_discount += rental["discount"]

    print("Total Rentals:", total_rentals)
    print("Active Rentals:", active_rentals)
    print("Returned Rentals:", returned_rentals)
    print(f"Total Discount Given: ₹{total_discount:.2f}")
    print(f"Total Rental Revenue: ₹{total_revenue:.2f}")

    


# MAIN MENU 

def main():
    while True:
        print("\n__VEHICLE RENTAL MANAGEMENT SYSTEM__")
        print("1. Add New Vehicle")
        print("2. View All Available Vehicles")
        print("3. Rent a Vehicle")
        print("4. Return a Vehicle")
        print("5. Search Rental Details using Customer ID")
        print("6. Display All Rented Vehicles")
        print("7. Generate Rental Summary Report")
        print("8. Exit")
        

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_vehicle()

        elif choice == "2":
            view_available_vehicles()

        elif choice == "3":
            rent_vehicle()

        elif choice == "4":
            return_vehicle()

        elif choice == "5":
            search_rental()

        elif choice == "6":
            display_rented_vehicles()

        elif choice == "7":
            rental_summary_report()

        elif choice == "8":
            print("Thank you for using Vehicle Rental Management System.")
            break

        else:
            print("Invalid choice. Please select 1 to 8.")


# Start the program
main()