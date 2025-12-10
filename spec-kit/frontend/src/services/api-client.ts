// Type definitions matching the backend API contracts

export interface TextbookGenerationRequest {
  subject: string;
  title: string;
  educational_level: 'K12' | 'UNDERGRADUATE' | 'GRADUATE';
  settings?: {
    include_exercises?: boolean;
    include_summaries?: boolean;
    output_format?: string;
    custom_style?: string;
    chapters_count?: number;
  };
}

export interface TextbookGenerationResponse {
  id: string;
  status: string;
  created_at: string;
  estimated_completion?: string;
}

export interface Textbook {
  id: string;
  title: string;
  subject: string;
  educational_level: string;
  status: string;
  created_at: string;
  updated_at: string;
  chapters_count: number;
  settings: Record<string, any>;
  chapters: Chapter[];
}

export interface Section {
  id: string;
  title: string;
  content: string;
  position: number;
  created_at: string;
  updated_at: string;
  type: string;
  chapter_id: string;
}

export interface Chapter {
  id: string;
  title: string;
  content?: string;
  position: number;
  created_at: string;
  updated_at: string;
  status: string;
  textbook_id: string;
  sections: Section[];
}

export interface UpdateChapterRequest {
  title: string;
  content: string;
  status: string;
}

export interface UserPreferences {
  default_educational_level: string;
  default_format: string;
  default_style: string;
  include_exercises_by_default: boolean;
  include_summaries_by_default: boolean;
  updated_at: string;
}

// Mock API client implementation
// In a real implementation, this would make actual HTTP requests to the backend

class ApiClient {
  private baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

  private async apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Network error' }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async generateTextbook(data: TextbookGenerationRequest): Promise<TextbookGenerationResponse> {
    return this.apiRequest<TextbookGenerationResponse>('/textbook/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getTextbook(textbookId: string): Promise<Textbook> {
    return this.apiRequest<Textbook>(`/textbook/${textbookId}`, {
      method: 'GET',
    });
  }

  async updateChapter(chapterId: string, data: UpdateChapterRequest): Promise<Chapter> {
    return this.apiRequest<Chapter>(`/chapter/${chapterId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async exportTextbook(textbookId: string, format: string): Promise<{download_url: string, expires_at: string}> {
    const response = await this.apiRequest<any>(`/textbook/${textbookId}/export`, {
      method: 'POST',
      body: JSON.stringify({ format }),
    });

    // Return the expected format
    return {
      download_url: response.download_url,
      expires_at: response.expires_at
    };
  }

  async getUserPreferences(): Promise<UserPreferences> {
    return this.apiRequest<UserPreferences>('/user/preferences', {
      method: 'GET',
    });
  }

  async updateUserPreferences(data: Omit<UserPreferences, 'updated_at'>): Promise<UserPreferences> {
    return this.apiRequest<UserPreferences>('/user/preferences', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async updateSection(sectionId: string, data: Partial<{title: string, content: string, type: string}>): Promise<any> {
    const response = await this.apiRequest<any>(`/section/${sectionId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });

    return response;
  }

  async addSection(chapterId: string, data: {title: string, content: string, type: string, position?: number}): Promise<any> {
    const response = await this.apiRequest<any>(`/chapter/${chapterId}/section`, {
      method: 'POST',
      body: JSON.stringify(data),
    });

    return response;
  }

  async deleteSection(sectionId: string): Promise<any> {
    return this.apiRequest<any>(`/section/${sectionId}`, {
      method: 'DELETE',
    });
  }
}

export default new ApiClient();