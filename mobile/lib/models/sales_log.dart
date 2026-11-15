class SalesLog {
  const SalesLog({
    required this.id,
    required this.salesDate,
    required this.repName,
    required this.productName,
    required this.quantity,
    required this.amount,
    this.hospitalName = '',
    this.pharmacyName = '',
    this.reference = '',
    this.notes = '',
  });

  final int id;
  final String salesDate;
  final String repName;
  final String productName;
  final int quantity;
  final double amount;
  final String hospitalName;
  final String pharmacyName;
  final String reference;
  final String notes;

  factory SalesLog.fromJson(Map<String, dynamic> json) => SalesLog(
        id: json['id'] as int,
        salesDate: json['sales_date'] as String? ?? '',
        repName: json['rep_name'] as String? ?? '',
        productName: json['product_name'] as String? ?? '',
        quantity: json['quantity'] as int? ?? 0,
        amount: double.tryParse('${json['amount']}') ?? 0,
        hospitalName: json['hospital_name'] as String? ?? '',
        pharmacyName: json['pharmacy_name'] as String? ?? '',
        reference: json['reference'] as String? ?? '',
        notes: json['notes'] as String? ?? '',
      );
}
