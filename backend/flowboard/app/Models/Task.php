<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Task extends Model
{
    protected $fillable = [
        "description",
        "tasklist_id",
        "order",
        "done"
    ];

    public function tasklist(): BelongsTo
    {
        return $this->belongsTo(Tasklist::class);
    }

    public function scopeOwnedBy($query, User $user)
    {
        return $query->whereHas('tasklist.workspace', function ($q) use ($user) {
            $q->where('user_id', $user->id);
        });
    }
}