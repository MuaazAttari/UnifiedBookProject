import ApiClient from './api-client';

describe('ApiClient', () => {
  test('should generate textbook with mock API', async () => {
    const requestData = {
      subject: 'Test Subject',
      title: 'Test Title',
      educational_level: 'UNDERGRADUATE' as const
    };

    const result = await ApiClient.generateTextbook(requestData);

    expect(result).toHaveProperty('id');
    expect(result).toHaveProperty('status');
    expect(result.status).toBe('GENERATING');
  });

  test('should get textbook with mock API', async () => {
    const textbookId = 'test-id';

    const result = await ApiClient.getTextbook(textbookId);

    expect(result).toHaveProperty('id');
    expect(result.id).toBe(textbookId);
    expect(result).toHaveProperty('title');
  });

  test('should update chapter with mock API', async () => {
    const chapterId = 'chapter-id';
    const updateData = {
      title: 'Updated Title',
      content: 'Updated content',
      status: 'REVIEWED'
    };

    const result = await ApiClient.updateChapter(chapterId, updateData);

    expect(result).toHaveProperty('id');
    expect(result.id).toBe(chapterId);
    expect(result.title).toBe(updateData.title);
  });
});