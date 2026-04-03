<?php

namespace App\Services\AI\Retrieval;

use App\Services\AI\Retrieval\DTO\ChunkDTO;
use App\Services\AI\Retrieval\DTO\TaskListDTO;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class RetrievalService
{
    public function retrieveLists(string $query, int $userId): array
    {
        $response = Http::ai()->post("/retrieval/lists", [
            'query' => $query,
            'user_id' => $userId,
            'type' => 'collection'
        ]);

        $data = $response->json();

        return collect($data['lists'])->map(function ($list) {
            return new TaskListDTO(
                tasklist_id: (int) $list['tasklist_id'],
                score: (float) $list['score'],
                relevance: (float) $list['relevance'],
                volume: (int) $list['volume'],
                concentration: (float) $list['concentration'],
                volume_norm: (float) $list['volume_norm'],
                chunks: collect($list['chunks'])->map(
                    fn($chunk) =>
                    new ChunkDTO(
                        chunk_id: (int) $chunk['chunk_id'],
                        score: (float) $chunk['score'],
                    )
                )->toArray()
            );
        })->toArray();
    }
}
