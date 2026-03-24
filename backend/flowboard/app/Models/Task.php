<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Task extends Model
{
    use HasFactory;

    protected $fillable = [
        "description",
        "tasklist_id",
        "order",
        "done",
        "user_id"
    ];

    public function tasklist(): BelongsTo
    {
        return $this->belongsTo(Tasklist::class);
    }

    public function scopeOwnedBy($query, User $user)
    {
        return $query->where('user_id', $user->id);
    }
}