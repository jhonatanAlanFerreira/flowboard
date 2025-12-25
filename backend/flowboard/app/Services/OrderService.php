<?php

namespace App\Services;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\DB;

class OrderService
{
    /**
     * Reorder items by explicit ID list (same parent)
     *
     * @param class-string<Model> $model
     * @param array<int> $ids
     * @param array<string, mixed> $scope
     */
    public function reorder(
        string $model,
        array $ids,
        array $scope = []
    ): void {
        DB::transaction(function () use ($model, $ids, $scope) {

            $baseQuery = $model::query();

            foreach ($scope as $column => $value) {
                $baseQuery->where($column, $value);
            }

            foreach ($ids as $index => $id) {
                (clone $baseQuery)
                    ->where('id', $id)
                    ->update(['order' => $index + 1]);
            }
        });
    }

    /**
     * Delete record and fix sibling order
     */
    public function deleteAndFixOrder(
        Model $record,
        string $foreignKey
    ): void {
        DB::transaction(function () use ($record, $foreignKey) {

            $modelClass = $record::class;
            $foreignId = $record->{$foreignKey};
            $deletedOrder = $record->order;

            $record->delete();

            if ($deletedOrder === null) {
                return;
            }

            $modelClass::where($foreignKey, $foreignId)
                ->where('order', '>', $deletedOrder)
                ->decrement('order');
        });
    }

    /**
     * Move items between parents and reorder target
     *
     * @param class-string<Model> $model
     * @param string $foreignKey
     * @param int $sourceId
     * @param int $targetId
     * @param array<int> $orderedIds
     * @param array<string, mixed> $scope
     */
    public function moveAndReorder(
        string $model,
        string $foreignKey,
        int $sourceId,
        int $targetId,
        array $orderedIds,
        array $scope = []
    ): void {
        DB::transaction(function () use ($model, $foreignKey, $sourceId, $targetId, $orderedIds, $scope) {

            $baseQuery = $model::query();

            foreach ($scope as $column => $value) {
                $baseQuery->where($column, $value);
            }

            foreach ($orderedIds as $index => $id) {
                (clone $baseQuery)
                    ->where('id', $id)
                    ->update([
                        $foreignKey => $targetId,
                        'order' => $index + 1,
                    ]);
            }

            if ($sourceId !== $targetId) {
                $this->normalize(
                    $model,
                    $foreignKey,
                    $sourceId,
                    $scope
                );
            }
        });
    }

    /**
     * Normalize order sequence (1..N)
     *
     * @param class-string<Model> $model
     */
    public function normalize(
        string $model,
        string $foreignKey,
        int $foreignId,
        array $scope = []
    ): void {
        $query = $model::where($foreignKey, $foreignId);

        foreach ($scope as $column => $value) {
            $query->where($column, $value);
        }

        $query->orderBy('order')
            ->get()
            ->each(
                fn($item, $i) =>
                $item->update(['order' => $i + 1])
            );
    }
}
