<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ChunkTag extends Model
{
    use HasFactory;

    protected $table = 'chunk_tags';

    /**
     * Mass assignable attributes
     */
    protected $fillable = [
        'name',
    ];
}
