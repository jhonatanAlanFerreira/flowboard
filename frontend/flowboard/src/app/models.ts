export interface Workspace {
  id: number;
  name: string;
}

export interface Task {
  id: number;
  description: string;
  order: number;
  done: boolean;
  tasklist_id: number;
}

export interface Tasklist {
  id: number;
  order: number;
  name: string;
  tasks?: Task[];
}
