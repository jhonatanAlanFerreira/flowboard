<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Relations\HasOne;

class Workspace extends Model
{
    use HasFactory;

    protected $fillable = [
        "name",
        "user_id",
        "workspace_category_id"
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function tasklists(): HasMany
    {
        return $this->hasMany(Tasklist::class)->orderBy('order');
    }

    public function chunk(): HasOne
    {
        return $this->hasOne(RagChunk::class)
            ->where('type', 'workspace');
    }

    public function category(): BelongsTo
    {
        return $this->belongsTo(Category::class, 'workspace_category_id');
    }
}
