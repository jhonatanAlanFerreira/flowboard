<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Task extends Model
{
    public function tasklist(): BelongsTo
    {
        return $this->belongsTo(Tasklist::class);
    }
}