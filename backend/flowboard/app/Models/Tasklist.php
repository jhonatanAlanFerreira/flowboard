<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Tasklist extends Model
{
    protected $fillable = [
        "name",
        "workspace_id",
        "order"
    ];

    public function workspace(): BelongsTo
    {
        return $this->belongsTo(Workspace::class);
    }

    public function tasks(): HasMany
    {
        return $this->hasMany(Task::class)->orderBy('order');
    }

    public function scopeOwnedBy($query, User $user)
    {
        return $query->whereHas('workspace', function ($q) use ($user) {
            $q->where('user_id', $user->id);
        });
    }
}