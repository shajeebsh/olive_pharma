import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../models/masters.dart';
import '../../../providers/masters_providers.dart';

final _dateFormat = DateFormat('EEE, d MMM yyyy');

class DateField extends StatelessWidget {
  const DateField({
    super.key,
    required this.value,
    required this.onChanged,
  });

  final DateTime value;
  final ValueChanged<DateTime> onChanged;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () async {
        final today = DateTime.now();
        final picked = await showDatePicker(
          context: context,
          initialDate: value,
          firstDate: DateTime(2020),
          lastDate: DateTime(today.year, today.month, today.day),
          helpText: 'Visit date (no future dates)',
        );
        if (picked != null) onChanged(picked);
      },
      child: InputDecorator(
        decoration: const InputDecoration(
          labelText: 'Date',
          prefixIcon: Icon(Icons.calendar_today_outlined),
        ),
        child: Text(_dateFormat.format(value)),
      ),
    );
  }
}

/// Dependent region dropdown.
class RegionDropdown extends ConsumerWidget {
  const RegionDropdown({
    super.key,
    required this.value,
    required this.onChanged,
  });

  final int? value;
  final ValueChanged<int?> onChanged;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final regions = ref.watch(regionsProvider);
    return DropdownButtonFormField<int>(
      value: value,
      isExpanded: true,
      decoration: const InputDecoration(labelText: 'Region'),
      items: regions.maybeWhen(
        data: (list) => list
            .map((r) => DropdownMenuItem(value: r.id, child: Text(r.name)))
            .toList(),
        orElse: () => const [],
      ),
      onChanged: onChanged,
      validator: (v) => v == null ? 'Select a region' : null,
    );
  }
}

/// Hospitals filtered by the selected region.
class HospitalDropdown extends ConsumerWidget {
  const HospitalDropdown({
    super.key,
    required this.regionId,
    required this.value,
    required this.onChanged,
  });

  final int? regionId;
  final int? value;
  final ValueChanged<int?> onChanged;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final hospitals = regionId == null
        ? const AsyncValue<List<Hospital>>.data([])
        : ref.watch(hospitalsProvider(regionId));
    return DropdownButtonFormField<int>(
      value: value,
      isExpanded: true,
      decoration: const InputDecoration(labelText: 'Hospital'),
      items: hospitals.maybeWhen(
        data: (list) => list
            .map((h) => DropdownMenuItem(value: h.id, child: Text(h.name)))
            .toList(),
        orElse: () => const [],
      ),
      onChanged: regionId == null ? null : onChanged,
      validator: (v) => v == null ? 'Select a hospital' : null,
    );
  }
}

/// Doctors filtered by the selected hospital.
class DoctorDropdown extends ConsumerWidget {
  const DoctorDropdown({
    super.key,
    required this.hospitalId,
    required this.value,
    required this.onChanged,
  });

  final int? hospitalId;
  final int? value;
  final ValueChanged<int?> onChanged;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final doctors = hospitalId == null
        ? const AsyncValue<List<Doctor>>.data([])
        : ref.watch(doctorsProvider(hospitalId));
    return DropdownButtonFormField<int>(
      value: value,
      isExpanded: true,
      decoration: const InputDecoration(labelText: 'Doctor'),
      items: doctors.maybeWhen(
        data: (list) => list
            .map((d) => DropdownMenuItem(value: d.id, child: Text(d.displayName)))
            .toList(),
        orElse: () => const [],
      ),
      onChanged: hospitalId == null ? null : onChanged,
      validator: (v) => v == null ? 'Select a doctor' : null,
    );
  }
}

/// Pharmacies filtered by the selected hospital.
class PharmacyDropdown extends ConsumerWidget {
  const PharmacyDropdown({
    super.key,
    required this.hospitalId,
    required this.value,
    required this.onChanged,
  });

  final int? hospitalId;
  final int? value;
  final ValueChanged<int?> onChanged;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pharmacies = hospitalId == null
        ? const AsyncValue<List<Pharmacy>>.data([])
        : ref.watch(pharmaciesProvider(hospitalId));
    return DropdownButtonFormField<int>(
      value: value,
      isExpanded: true,
      decoration: const InputDecoration(labelText: 'Pharmacy'),
      items: pharmacies.maybeWhen(
        data: (list) => list
            .map((p) => DropdownMenuItem(value: p.id, child: Text(p.name)))
            .toList(),
        orElse: () => const [],
      ),
      onChanged: hospitalId == null ? null : onChanged,
      validator: (v) => v == null ? 'Select a pharmacy' : null,
    );
  }
}

/// Multi-select product picker rendered as toggleable chips.
class ProductMultiSelect extends ConsumerWidget {
  const ProductMultiSelect({
    super.key,
    required this.label,
    required this.selected,
    required this.onToggle,
  });

  final String label;
  final Set<int> selected;
  final void Function(int id, bool isSelected) onToggle;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final products = ref.watch(productsProvider);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: Theme.of(context).textTheme.labelLarge),
        const SizedBox(height: 8),
        products.when(
          loading: () => const Padding(
            padding: EdgeInsets.symmetric(vertical: 12),
            child: LinearProgressIndicator(),
          ),
          error: (e, _) => Text('Could not load products: $e'),
          data: (list) => list.isEmpty
              ? const Text('No active products available.')
              : Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    for (final product in list)
                      FilterChip(
                        label: Text(product.name),
                        selected: selected.contains(product.id),
                        onSelected: (value) => onToggle(product.id, value),
                      ),
                  ],
                ),
        ),
      ],
    );
  }
}
