class PagedResult<T> {
  const PagedResult({required this.items, required this.hasMore});

  final List<T> items;
  final bool hasMore;
}

class SelectOption {
  const SelectOption({required this.id, required this.text});

  final int id;
  final String text;

  factory SelectOption.fromJson(Map<String, dynamic> json) => SelectOption(
        id: json['id'] as int,
        text: json['text'] as String? ?? '',
      );
}
