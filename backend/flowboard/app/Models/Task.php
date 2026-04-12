<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Relations\HasOne;
use Illuminate\Database\Eloquent\Relations\HasOneThrough;

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

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function chunk(): HasOne
    {
        return $this->hasOne(RagChunk::class);
    }

    public function workspace(): HasOneThrough
    {
        return $this->hasOneThrough(
            Workspace::class,
            Tasklist::class,
            'id',
            'id',
        );
    }

    public function scopeOwnedBy($query, User $user)
    {
        return $query->where('user_id', $user->id);
    }
}
