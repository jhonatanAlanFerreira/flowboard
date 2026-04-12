<?php

namespace App\Enums;

enum AIJobsType: string
{
    case COLLECTION_WORKSPACE = 'collection_workspace';
    case WORKFLOW_WORKSPACE = 'workflow_workspace';
    case USER_QUESTION = 'user_question';
}
