import 'package:flutter/material.dart';

import 'chemist_visits_tab.dart';
import 'doctor_visits_tab.dart';

class VisitsHubScreen extends StatelessWidget {
  const VisitsHubScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Visits'),
          bottom: const TabBar(
            indicatorColor: Colors.white,
            labelColor: Colors.white,
            unselectedLabelColor: Colors.white70,
            tabs: [
              Tab(text: 'Meet Doctor'),
              Tab(text: 'Meet Chemist'),
            ],
          ),
        ),
        body: const TabBarView(
          children: [
            DoctorVisitsTab(),
            ChemistVisitsTab(),
          ],
        ),
      ),
    );
  }
}
