<?php

namespace Tests\Feature\Jobs\AI\Task;

use App\DTOs\AI\RagChunkDTO;
use App\Enums\RagChunkType;
use App\Jobs\AI\Task\GenerateTaskChunkJob;
use App\Models\RagChunk;
use App\Models\Task;
use App\Services\AI\Agents\TaggingAgent;
use App\Services\Chunking\Builders\TaskChunkBuilder;
use App\Services\Chunking\ChunkService;
use Tests\TestCase;

class GenerateTaskChunkJobTest extends TestCase
{
    public function test_it_handles_task_chunk_generation_and_tagging()
    {
        $task = Task::factory()->make(['id' => 1]);

        $mockDto = new RagChunkDTO(
            user_id: 1,
            type: RagChunkType::TASK,
            workspace_id: 10,
            tasklist_id: 5,
            task_id: 1,
            content: 'Test content'
        );

        $mockChunkModel = new RagChunk(['id' => 99]);

        // Create Mocks
        $taskChunkBuilder = $this->createMock(TaskChunkBuilder::class);
        $chunkService = $this->createMock(ChunkService::class);
        $taggingAgent = $this->createMock(TaggingAgent::class);

        // Define expectations
        $taskChunkBuilder->expects($this->once())
            ->method('build')
            ->with($task)
            ->willReturn($mockDto);

        $chunkService->expects($this->once())
            ->method('upsertChunk')
            ->with($mockDto)
            ->willReturn($mockChunkModel);

        $taggingAgent->expects($this->once())
            ->method('generateTags')
            ->with($mockChunkModel);

        // Execute job handle
        $job = new GenerateTaskChunkJob($task);

        $job->handle($chunkService, $taskChunkBuilder, $taggingAgent);
    }
}
