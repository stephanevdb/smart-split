import { API_BASE_URL } from '../config/environment';

export interface HealthStatus {
  status: string;
  message: string;
  version: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  iban: string;
  bic: string;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name: string;
  iban: string;
  bic: string;
}

export interface UpdateProfileRequest {
  full_name: string;
  iban: string;
  bic: string;
}

export interface Group {
  id: string;
  name: string;
  description: string;
  created_by: number;
  invite_code: string;
  created_at: string;
  member_count: number;
}

export interface CreateGroupRequest {
  name: string;
  description: string;
}

export interface UpdateGroupRequest {
  name: string;
  description: string;
}

export interface GroupMember {
  id: number;
  group_id: string;
  user_id: number;
  joined_at: string;
  user?: User;
}

export interface JoinGroupRequest {
  invite_code: string;
}

export interface AuthResponse {
  message: string;
  user: User;
  token: string;
}


export interface ProfileResponse {
  user: User;
}

export class ApiService {
  private static instance: ApiService;
  private isOnline = true;
  private lastCheck = 0;
  private readonly CHECK_INTERVAL = 30000; // 30 seconds
  private authToken: string | null = null;

  private constructor() {
    console.log('ApiService initialized, starting health checks...');
    this.loadAuthToken();
    this.startHealthCheck();
  }

  public static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  // Token management methods
  private loadAuthToken(): void {
    this.authToken = localStorage.getItem('authToken');
  }

  public setAuthToken(token: string): void {
    this.authToken = token;
    localStorage.setItem('authToken', token);
  }

  public clearAuthToken(): void {
    this.authToken = null;
    localStorage.removeItem('authToken');
  }

  public getAuthToken(): string | null {
    return this.authToken;
  }

  public isAuthenticated(): boolean {
    return this.authToken !== null;
  }

  public logout(): void {
    this.clearAuthToken();
    localStorage.removeItem('currentUser');
  }

  // Helper method to get headers with auth token
  private getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    };
    
    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }
    
    return headers;
  }

  public async checkHealth(): Promise<HealthStatus> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        },
        signal: AbortSignal.timeout(5000) // 5 second timeout
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.isOnline = true;
      this.lastCheck = Date.now();
      return data;
    } catch (error) {
      console.error('API health check failed:', error);
      this.isOnline = false;
      this.lastCheck = Date.now();
      throw error;
    }
  }

  public async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials),
        signal: AbortSignal.timeout(10000) // 10 second timeout
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Login failed');
      }

      const authResponse = await response.json();
      
      // Store the token
      if (authResponse.token) {
        this.setAuthToken(authResponse.token);
      }

      return authResponse;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  public async register(userData: RegisterRequest): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData),
        signal: AbortSignal.timeout(10000) // 10 second timeout
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Registration failed');
      }

      const authResponse = await response.json();
      
      // Store the token
      if (authResponse.token) {
        this.setAuthToken(authResponse.token);
      }

      return authResponse;
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }


  public async getProfile(): Promise<ProfileResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/profile`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
        signal: AbortSignal.timeout(10000) // 10 second timeout
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch profile');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      throw error;
    }
  }

  public async updateProfile(profileData: UpdateProfileRequest): Promise<ProfileResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/profile`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(profileData),
        signal: AbortSignal.timeout(10000) // 10 second timeout
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to update profile');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to update profile:', error);
      throw error;
    }
  }

  public isApiOnline(): boolean {
    console.log('API online status:', this.isOnline);
    return this.isOnline;
  }

  public getLastCheck(): number {
    return this.lastCheck;
  }

  // Group methods
  public async getGroups(): Promise<{ groups: Group[] }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/groups`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
        signal: AbortSignal.timeout(10000)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch groups');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch groups:', error);
      throw error;
    }
  }

  public async createGroup(groupData: CreateGroupRequest): Promise<{ message: string; group: Group }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/groups`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(groupData),
        signal: AbortSignal.timeout(10000)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create group');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to create group:', error);
      throw error;
    }
  }

  public async getGroup(groupId: string): Promise<{ group: Group; members: GroupMember[] }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/groups/${groupId}`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
        signal: AbortSignal.timeout(10000)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch group');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch group:', error);
      throw error;
    }
  }

  public async updateGroup(groupId: string, groupData: UpdateGroupRequest): Promise<{ message: string; group: Group }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/groups/${groupId}`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(groupData),
        signal: AbortSignal.timeout(10000)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to update group');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to update group:', error);
      throw error;
    }
  }

  public async deleteGroup(groupId: string): Promise<{ message: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/groups/${groupId}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders(),
        signal: AbortSignal.timeout(10000)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete group');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to delete group:', error);
      throw error;
    }
  }

  public async joinGroup(joinData: JoinGroupRequest): Promise<{ message: string; group: Group }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/groups/join`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(joinData),
        signal: AbortSignal.timeout(10000)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to join group');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to join group:', error);
      throw error;
    }
  }

  public async leaveGroup(groupId: string): Promise<{ message: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/groups/${groupId}/leave`, {
        method: 'DELETE',
        headers: this.getAuthHeaders(),
        signal: AbortSignal.timeout(10000)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to leave group');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to leave group:', error);
      throw error;
    }
  }

  private startHealthCheck(): void {
    console.log('Starting health check interval...');
    // Initial check
    this.checkHealth().catch((error) => {
      console.error('Initial health check failed:', error);
    });

    // Periodic health checks
    setInterval(async () => {
      try {
        await this.checkHealth();
      } catch (error) {
        console.error('Periodic health check failed:', error);
      }
    }, this.CHECK_INTERVAL);
  }
}

export const apiService = ApiService.getInstance();
