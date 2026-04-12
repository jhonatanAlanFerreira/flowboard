export interface Workspace {
  id: number;
  name: string;
}

export interface Task {
  id: number;
  description: string;
  order: number;
  done: boolean;
  tasklist?: Tasklist;
  tasklist_id: number;
  matchesSearch: boolean;
}

export interface Tasklist {
  id: number;
  order: number;
  name: string;
  tasks?: Task[];
  workspace?: Workspace;
  hasMatchingTasks: boolean;
}

export interface User {
  id: number;
  name: string;
  email: string;
}
