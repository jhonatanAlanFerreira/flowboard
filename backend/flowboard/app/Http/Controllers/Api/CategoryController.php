<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\CategoryController\StoreCategoryRequest;
use App\Models\Category;
use Illuminate\Http\Request;

class CategoryController extends Controller
{
    public function store(StoreCategoryRequest $request)
    {
        return Category::create([
            'name' => $request->validated()['name'],
            'user_id' => $request->user()->id,
        ]);
    }

    public function userCategories(Request $request)
    {
        return $request->user()->categories;
    }
}
