import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:sajilochat/main.dart';

void main() {
  testWidgets('Login screen smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(SajiloChat());

    // Verify that login screen elements are present
    expect(find.text('Sajilo Chat'), findsOneWidget);
    expect(find.text('Welcome back!'), findsOneWidget);
    expect(find.text('Login'), findsOneWidget);
  });
}