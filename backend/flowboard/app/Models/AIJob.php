<?php

namespace App\Models;

use App\Enums\AIJobsType;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class AIJob extends Model
{
    use HasFactory;

    protected $table = 'ai_jobs';

    protected $fillable = [
        'user_id',
        'status',
        'prompt',
        'workspace_id',
        'type',
        'metadata',
        'workspace_category_id'
    ];

    protected $casts = [
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
        'metadata' => 'array',
        'type' => AIJobsType::class
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function workspace()
    {
        return $this->belongsTo(Workspace::class);
    }

    public function isPending(): bool
    {
        return $this->status === 'pending';
    }

    public function isDone(): bool
    {
        return $this->status === 'done';
    }

    public function isFailed(): bool
    {
        return $this->status === 'failed';
    }

    public function scopeIsWorkspaceGeneration(Builder $query): void
    {
        $query->whereIn('type', [
            AIJobsType::COLLECTION_WORKSPACE,
            AIJobsType::WORKFLOW_WORKSPACE
        ]);
    }

    public function scopeIsDataQuestion($query)
    {
        return $query->where('type', AIJobsType::USER_QUESTION);
    }

    public function category(): BelongsTo
    {
        return $this->belongsTo(Category::class, 'workspace_category_id');
    }
}
