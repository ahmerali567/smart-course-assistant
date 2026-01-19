import difflib

def fuzzy_search_topics(query, topics, threshold=0.6, top_n=5):
    """
    Perform fuzzy search on topics using difflib.
    Returns a list of tuples: (topic, similarity_score) for matches above threshold, sorted by score descending, limited to top_n.
    """
    matches = []
    query_lower = query.lower()
    for topic in topics:
        topic_name_lower = topic.name.lower()
        ratio = difflib.SequenceMatcher(None, query_lower, topic_name_lower).ratio()
        if ratio >= threshold:
            matches.append((topic, ratio))
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:top_n]
