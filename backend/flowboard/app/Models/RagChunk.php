<?php

namespace App\Models;

use App\Enums\ChunkType;
use Illuminate\Database\Eloquent\Model;

class RagChunk extends Model
{
    protected $table = 'rag_chunks';

    protected $fillable = [
        'user_id',
        'workspace_id',
        'tasklist_id',
        'task_id',
        'type',
        'content',
        'metadata',
        'is_durty',
        'has_embedding',
    ];

    protected $casts = [
        'metadata' => 'array',
        'is_durty' => 'boolean',
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

    public function scopeTasks($query)
    {
        return $query->where('type', ChunkType::TASK->value);
    }

    public function scopeListPatterns($query)
    {
        return $query->where('type', ChunkType::TAG_GROUP->value);
    }

    public function scopeWorkspacePatterns($query)
    {
        return $query->where('type', ChunkType::PATTERN_STRUCTURE->value);
    }

    public function scopeDirty($query)
    {
        return $query->where('is_durty', true);
    }

    public function scopeWithoutEmbedding($query)
    {
        return $query->where('has_embedding', false);
    }

    public function markClean(): void
    {
        $this->update(['is_durty' => false]);
    }

    public function markDirty(): void
    {
        $this->update(['is_durty' => true]);
    }

    public function markEmbedded(): void
    {
        $this->update(['has_embedding' => true]);
    }
}
