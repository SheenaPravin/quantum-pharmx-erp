import 'package:flutter/material.dart';

void main() => runApp(const PharmXApp());

class PharmXApp extends StatelessWidget {
  const PharmXApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Quantum PharmX BI',
      home: Scaffold(
        appBar: AppBar(title: const Text('Quantum PharmX™ BI')),
        body: const Center(child: Text('Approvals • QC • Warehouse • Production (API: /api/v1)')),
      ),
    );
  }
}
