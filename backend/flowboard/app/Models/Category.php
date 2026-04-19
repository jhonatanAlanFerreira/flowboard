<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Category extends Model
{
    use HasFactory;

    protected $table = 'workspace_categories';

    /**
     * Mass assignable attributes
     */
    protected $fillable = [
        'name',
        'user_id'
    ];
}
