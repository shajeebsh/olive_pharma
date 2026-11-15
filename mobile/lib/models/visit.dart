import 'masters.dart';

class DoctorVisit {
  const DoctorVisit({
    required this.id,
    required this.date,
    required this.regionName,
    required this.hospitalName,
    required this.doctorName,
    this.products = const [],
    this.notes = '',
  });

  final int id;
  final String date;
  final String regionName;
  final String hospitalName;
  final String doctorName;
  final List<Product> products;
  final String notes;

  factory DoctorVisit.fromJson(Map<String, dynamic> json) => DoctorVisit(
        id: json['id'] as int,
        date: json['date'] as String? ?? '',
        regionName: json['region_name'] as String? ?? '',
        hospitalName: json['hospital_name'] as String? ?? '',
        doctorName: json['doctor_name'] as String? ?? '',
        products: (json['products_introduced_detail'] as List<dynamic>? ?? [])
            .map((e) => Product.fromJson(e as Map<String, dynamic>))
            .toList(),
        notes: json['notes'] as String? ?? '',
      );
}

class ChemistVisit {
  const ChemistVisit({
    required this.id,
    required this.date,
    required this.regionName,
    required this.hospitalName,
    required this.pharmacyName,
    this.doctorName = '',
    this.currentProducts = '',
    this.productsNeeded = const [],
    this.quantity = 1,
    this.notes = '',
  });

  final int id;
  final String date;
  final String regionName;
  final String hospitalName;
  final String pharmacyName;
  final String doctorName;
  final String currentProducts;
  final List<Product> productsNeeded;
  final int quantity;
  final String notes;

  factory ChemistVisit.fromJson(Map<String, dynamic> json) => ChemistVisit(
        id: json['id'] as int,
        date: json['date'] as String? ?? '',
        regionName: json['region_name'] as String? ?? '',
        hospitalName: json['hospital_name'] as String? ?? '',
        pharmacyName: json['pharmacy_name'] as String? ?? '',
        doctorName: json['doctor_name'] as String? ?? '',
        currentProducts: json['current_products'] as String? ?? '',
        productsNeeded: (json['products_needed_detail'] as List<dynamic>? ?? [])
            .map((e) => Product.fromJson(e as Map<String, dynamic>))
            .toList(),
        quantity: json['quantity'] as int? ?? 1,
        notes: json['notes'] as String? ?? '',
      );
}
