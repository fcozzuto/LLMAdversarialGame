def choose_move(observation):
    # Defensive access to environment info
    grid = observation.get('grid', [])
    agent_pos = observation.get('agent_pos', (0, 0))
    agents = observation.get('agents', {})
    resources = observation.get('resources', {})
    enemies = observation.get('enemies', {})
    territory = observation.get('territory', {})

    ax, ay = agent_pos

    # Helper functions
    def in_bounds(x, y):
        return 0 <= x < len(grid) and 0 <= y < len(grid[0])

    def get_adjacent_positions(x, y):
        return [(x+dx, y+dy) for dx in [-1,0,1] for dy in [-1,0,1]
                if (dx != 0 or dy != 0) and in_bounds(x+dx, y+dy)]

    # Determine goals based on observation type
    # Priority: gather resources, pursue enemies, expand territory

    # 1. Check for resources in adjacent or nearby cells
    for (nx, ny) in get_adjacent_positions(ax, ay):
        if resources.get((nx, ny), 0):
            dx = nx - ax
            dy = ny - ay
            return [dx, dy]

    # 2. Pursue nearby enemies (if any)
    for (nx, ny) in get_adjacent_positions(ax, ay):
        if enemies.get((nx, ny), 0):
            dx = nx - ax
            dy = ny - ay
            return [dx, dy]

    # 3. Expand territory: move towards unclaimed or less controlled areas
    # identify the position with least territory influence nearby
    min_territory = float('inf')
    target = None
    for (nx, ny) in get_adjacent_positions(ax, ay):
        terr_value = territory.get((nx, ny), 0)
        if terr_value < min_territory:
            min_territory = terr_value
            target = (nx, ny)

    if target:
        dx = target[0] - ax
        dy = target[1] - ay
        return [dx, dy]

    # If no specific targets, stay put
    return [0, 0]
