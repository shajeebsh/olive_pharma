import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/api/api_exception.dart';
import '../../providers/core_providers.dart';
import 'widgets/form_fields.dart';

class ChemistVisitFormScreen extends ConsumerStatefulWidget {
  const ChemistVisitFormScreen({super.key});

  @override
  ConsumerState<ChemistVisitFormScreen> createState() =>
      _ChemistVisitFormScreenState();
}

class _ChemistVisitFormScreenState
    extends ConsumerState<ChemistVisitFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _currentProductsController = TextEditingController();
  final _quantityController = TextEditingController(text: '1');
  final _notesController = TextEditingController();
  final _iso = DateFormat('yyyy-MM-dd');

  DateTime _date = DateTime.now();
  int? _regionId;
  int? _hospitalId;
  int? _doctorId;
  int? _pharmacyId;
  final Set<int> _products = {};
  bool _submitting = false;
  String? _error;

  @override
  void dispose() {
    _currentProductsController.dispose();
    _quantityController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _submitting = true;
      _error = null;
    });
    try {
      await ref.read(visitRepositoryProvider).createChemistVisit({
        'date': _iso.format(_date),
        'region': _regionId,
        'hospital': _hospitalId,
        'doctor': _doctorId,
        'pharmacy': _pharmacyId,
        'current_products': _currentProductsController.text.trim(),
        'products_needed': _products.toList(),
        'quantity': int.tryParse(_quantityController.text) ?? 1,
        'notes': _notesController.text.trim(),
      });
      if (!mounted) return;
      Navigator.of(context).pop(true);
    } on ApiException catch (error) {
      setState(() => _error = error.message);
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('New Chemist Visit')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            DateField(value: _date, onChanged: (d) => setState(() => _date = d)),
            const SizedBox(height: 16),
            RegionDropdown(
              value: _regionId,
              onChanged: (value) => setState(() {
                _regionId = value;
                _hospitalId = null;
                _doctorId = null;
                _pharmacyId = null;
              }),
            ),
            const SizedBox(height: 16),
            HospitalDropdown(
              regionId: _regionId,
              value: _hospitalId,
              onChanged: (value) => setState(() {
                _hospitalId = value;
                _doctorId = null;
                _pharmacyId = null;
              }),
            ),
            const SizedBox(height: 16),
            DoctorDropdown(
              hospitalId: _hospitalId,
              value: _doctorId,
              onChanged: (value) => setState(() => _doctorId = value),
            ),
            const SizedBox(height: 16),
            PharmacyDropdown(
              hospitalId: _hospitalId,
              value: _pharmacyId,
              onChanged: (value) => setState(() => _pharmacyId = value),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _currentProductsController,
              decoration: const InputDecoration(
                labelText: 'Current products (optional)',
              ),
            ),
            const SizedBox(height: 20),
            ProductMultiSelect(
              label: 'Products needed',
              selected: _products,
              onToggle: (id, isSelected) => setState(() {
                if (isSelected) {
                  _products.add(id);
                } else {
                  _products.remove(id);
                }
              }),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _quantityController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Quantity requested'),
              validator: (value) {
                final parsed = int.tryParse(value ?? '');
                if (parsed == null || parsed < 1) return 'Enter a valid quantity';
                return null;
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _notesController,
              maxLines: 3,
              decoration: const InputDecoration(labelText: 'Notes (optional)'),
            ),
            if (_error != null) ...[
              const SizedBox(height: 16),
              Text(
                _error!,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            ],
            const SizedBox(height: 24),
            FilledButton(
              onPressed: _submitting ? null : _submit,
              child: _submitting
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Text('Save visit'),
            ),
          ],
        ),
      ),
    );
  }
}
