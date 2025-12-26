<?php

namespace App\Services;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\DB;

class OrderService
{
    /**
     * Reorder items by explicit ID list
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
     * Delete record and normalize siblings
     */
    public function deleteAndFixOrder(
        Model $record,
        string $foreignKey,
        array $scope = []
    ): void {
        DB::transaction(function () use ($record, $foreignKey, $scope) {

            $model = $record::class;
            $foreignId = $record->{$foreignKey};

            $record->delete();

            $this->normalize($model, [
                $foreignKey => $foreignId,
                ...$scope,
            ]);
        });
    }

    /**
     * Move items between parents and normalize both sides
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

            foreach ($orderedIds as $index => $id) {
                $model::where('id', $id)->update([
                    $foreignKey => $targetId,
                    'order' => $index + 1,
                ]);
            }

            $this->normalize($model, [
                $foreignKey => $targetId,
                ...$scope,
            ]);

            if ($sourceId !== $targetId) {
                $this->normalize($model, [
                    $foreignKey => $sourceId,
                    ...$scope,
                ]);
            }
        });
    }

    /**
     * Normalize order sequence (1..N) inside a scope
     */
    public function normalize(
        string $model,
        array $scope
    ): void {
        DB::transaction(function () use ($model, $scope) {

            $query = $model::query();

            foreach ($scope as $column => $value) {
                $query->where($column, $value);
            }

            $query->orderBy('order')
                ->pluck('id')
                ->each(function ($id, $index) use ($model, $scope) {
                    $update = $model::where('id', $id);

                    foreach ($scope as $column => $value) {
                        $update->where($column, $value);
                    }

                    $update->update(['order' => $index + 1]);
                });
        });
    }
}
