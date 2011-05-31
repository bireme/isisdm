function(doc) {
  emit(doc._id, doc.title);
};