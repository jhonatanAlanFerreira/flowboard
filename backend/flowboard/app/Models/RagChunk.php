<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class RagChunk extends Model
{
    protected $table = 'rag_chunks';

    protected $fillable = [
        'user_id',
        'workspace_id',
        'tasklist_id',
        'task_id',
        'content',
        'task_description',
        'metadata',
        'has_embedding',
    ];

    protected $casts = [
        'metadata' => 'array',
        'has_embedding' => 'boolean',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function workspace()
    {
        return $this->belongsTo(Workspace::class);
    }

    public function tasklist()
    {
        return $this->belongsTo(Tasklist::class);
    }

    public function task()
    {
        return $this->belongsTo(Task::class);
    }

    public function scopeWithoutEmbedding($query)
    {
        return $query->where('has_embedding', false);
    }

    public function markEmbedded(): void
    {
        $this->update(['has_embedding' => true]);
    }
}
