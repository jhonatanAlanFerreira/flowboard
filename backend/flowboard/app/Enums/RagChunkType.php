<?php

namespace App\Enums;

enum RagChunkType: string
{
    case TASK = 'task';
    case LIST = 'list';
    case WORKSPACE = 'workspace';
}
