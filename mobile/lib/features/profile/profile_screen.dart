import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api/api_exception.dart';
import '../../core/theme/app_theme.dart';
import '../../core/widgets/state_views.dart';
import '../../models/user_profile.dart';
import '../../providers/auth_controller.dart';
import '../../providers/core_providers.dart';
import '../../providers/masters_providers.dart';
import '../../providers/profile_provider.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authControllerProvider);
    final profile = ref.watch(profileProvider);
    final fallback = auth.user;

    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: profile.when(
        loading: () => fallback == null
            ? const LoadingView()
            : _ProfileForm(user: fallback),
        error: (error, _) => fallback == null
            ? ErrorView(
                message: '$error',
                onRetry: () => ref.invalidate(profileProvider),
              )
            : _ProfileForm(user: fallback),
        data: (user) => _ProfileForm(user: user),
      ),
    );
  }
}

class _ProfileForm extends ConsumerStatefulWidget {
  const _ProfileForm({required this.user});

  final UserProfile user;

  @override
  ConsumerState<_ProfileForm> createState() => _ProfileFormState();
}

class _ProfileFormState extends ConsumerState<_ProfileForm> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _phoneController;
  late final TextEditingController _employeeCodeController;
  int? _regionId;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _phoneController = TextEditingController(text: widget.user.phone);
    _employeeCodeController =
        TextEditingController(text: widget.user.employeeCode);
    _regionId = widget.user.region;
  }

  @override
  void dispose() {
    _phoneController.dispose();
    _employeeCodeController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);
    final messenger = ScaffoldMessenger.of(context);
    try {
      final updated = await ref.read(profileRepositoryProvider).update(
            phone: _phoneController.text.trim(),
            employeeCode: _employeeCodeController.text.trim(),
            region: _regionId,
          );
      ref.read(authControllerProvider.notifier).setUser(updated);
      ref.invalidate(profileProvider);
      messenger.showSnackBar(
        const SnackBar(content: Text('Profile updated.')),
      );
    } on ApiException catch (error) {
      messenger.showSnackBar(SnackBar(content: Text(error.message)));
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _logout() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Log out'),
        content: const Text('Are you sure you want to log out?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Log out'),
          ),
        ],
      ),
    );
    if (confirmed == true) {
      await ref.read(authControllerProvider.notifier).logout();
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final regions = ref.watch(regionsProvider);

    return Form(
      key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: AppTheme.primary.withOpacity(0.12),
                    child: Text(
                      widget.user.displayName.characters.first.toUpperCase(),
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.primary,
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          widget.user.displayName,
                          style: theme.textTheme.titleLarge
                              ?.copyWith(fontWeight: FontWeight.bold),
                        ),
                        Text(widget.user.username,
                            style: theme.textTheme.bodyMedium),
                        const SizedBox(height: 4),
                        Chip(
                          label: Text(widget.user.roleLabel),
                          visualDensity: VisualDensity.compact,
                          backgroundColor: AppTheme.primary.withOpacity(0.10),
                          side: BorderSide.none,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          TextFormField(
            controller: _phoneController,
            keyboardType: TextInputType.phone,
            decoration: const InputDecoration(
              labelText: 'Phone',
              prefixIcon: Icon(Icons.phone_outlined),
            ),
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _employeeCodeController,
            decoration: const InputDecoration(
              labelText: 'Employee code',
              prefixIcon: Icon(Icons.badge_outlined),
            ),
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<int>(
            value: _regionId,
            isExpanded: true,
            decoration: const InputDecoration(
              labelText: 'Region',
              prefixIcon: Icon(Icons.location_on_outlined),
            ),
            items: regions.maybeWhen(
              data: (list) => list
                  .map((r) => DropdownMenuItem(value: r.id, child: Text(r.name)))
                  .toList(),
              orElse: () => const [],
            ),
            onChanged: (value) => setState(() => _regionId = value),
          ),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: _saving ? null : _save,
            child: _saving
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                : const Text('Save changes'),
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: _logout,
            icon: const Icon(Icons.logout, color: AppTheme.danger),
            label: const Text('Log out',
                style: TextStyle(color: AppTheme.danger)),
          ),
        ],
      ),
    );
  }
}
