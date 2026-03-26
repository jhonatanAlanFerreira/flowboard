<?php

namespace App\Enums;

enum ChunkType: string
{
    case TASK = 'task';
    case TAG_GROUP = 'tag_group';
    case PATTERN_STRUCTURE = 'pattern_structure';
}
