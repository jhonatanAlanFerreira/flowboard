<?php

namespace App\Data;

class WorkspaceData
{
    public string $name;
    public array $lists;

    public function __construct(array $data)
    {
        $this->name = $data['workspace']['name'];
        $this->lists = $data['workspace']['lists'];
    }
}
