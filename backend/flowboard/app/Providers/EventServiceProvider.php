<?php

namespace App\Providers;

use App\Events\List\TasklistCreated;
use App\Events\List\TasklistDeleted;
use App\Events\List\TasklistUpdated;
use App\Events\Task\TaskCreated;
use App\Events\Task\TaskDeleted;
use App\Events\Task\TaskUpdated;
use App\Events\Workspace\WorkspaceCreated;
use App\Events\Workspace\WorkspaceDeleted;
use App\Events\Workspace\WorkspaceUpdated;
use App\Listeners\AI\HandleListAIProcessing;
use App\Listeners\AI\HandleTaskAIProcessing;
use App\Listeners\AI\HandleWorkspaceAIProcessing;
use Illuminate\Auth\Events\Registered;
use Illuminate\Auth\Listeners\SendEmailVerificationNotification;
use Illuminate\Foundation\Support\Providers\EventServiceProvider as ServiceProvider;
use Illuminate\Support\Facades\Event;

class EventServiceProvider extends ServiceProvider
{
    /**
     * The event to listener mappings for the application.
     *
     * @var array<class-string, array<int, class-string>>
     */
    protected $listen = [
        Registered::class => [
            SendEmailVerificationNotification::class,
        ],
        TaskCreated::class => [
            HandleTaskAIProcessing::class,
        ],
        TaskUpdated::class => [
            HandleTaskAIProcessing::class,
        ],
        TaskDeleted::class => [
            HandleTaskAIProcessing::class,
        ],
        TasklistDeleted::class => [
            HandleTaskAIProcessing::class
        ],

        TasklistCreated::class => [
            HandleListAIProcessing::class
        ],
        TasklistUpdated::class => [
            HandleListAIProcessing::class
        ],
        WorkspaceCreated::class => [
            HandleWorkspaceAIProcessing::class
        ],
        WorkspaceUpdated::class => [
            HandleWorkspaceAIProcessing::class
        ],
        WorkspaceDeleted::class => [
            HandleWorkspaceAIProcessing::class
        ],
    ];

    /**
     * Register any events for your application.
     */
    public function boot(): void
    {
        //
    }

    /**
     * Determine if events and listeners should be automatically discovered.
     */
    public function shouldDiscoverEvents(): bool
    {
        return false;
    }
}
