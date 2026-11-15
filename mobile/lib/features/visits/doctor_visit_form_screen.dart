import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/api/api_exception.dart';
import '../../providers/core_providers.dart';
import 'widgets/form_fields.dart';

class DoctorVisitFormScreen extends ConsumerStatefulWidget {
  const DoctorVisitFormScreen({super.key});

  @override
  ConsumerState<DoctorVisitFormScreen> createState() =>
      _DoctorVisitFormScreenState();
}

class _DoctorVisitFormScreenState
    extends ConsumerState<DoctorVisitFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _notesController = TextEditingController();
  final _iso = DateFormat('yyyy-MM-dd');

  DateTime _date = DateTime.now();
  int? _regionId;
  int? _hospitalId;
  int? _doctorId;
  final Set<int> _products = {};
  bool _submitting = false;
  String? _error;

  @override
  void dispose() {
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
      await ref.read(visitRepositoryProvider).createDoctorVisit({
        'date': _iso.format(_date),
        'region': _regionId,
        'hospital': _hospitalId,
        'doctor': _doctorId,
        'products_introduced': _products.toList(),
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
      appBar: AppBar(title: const Text('New Doctor Visit')),
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
              }),
            ),
            const SizedBox(height: 16),
            HospitalDropdown(
              regionId: _regionId,
              value: _hospitalId,
              onChanged: (value) => setState(() {
                _hospitalId = value;
                _doctorId = null;
              }),
            ),
            const SizedBox(height: 16),
            DoctorDropdown(
              hospitalId: _hospitalId,
              value: _doctorId,
              onChanged: (value) => setState(() => _doctorId = value),
            ),
            const SizedBox(height: 20),
            ProductMultiSelect(
              label: 'Products introduced',
              selected: _products,
              onToggle: (id, isSelected) => setState(() {
                if (isSelected) {
                  _products.add(id);
                } else {
                  _products.remove(id);
                }
              }),
            ),
            const SizedBox(height: 20),
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
