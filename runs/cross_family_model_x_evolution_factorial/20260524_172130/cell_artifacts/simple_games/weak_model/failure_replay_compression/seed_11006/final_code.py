def choose_move(observation):
    x, y = observation.get('self_position', [0, 0])
    w, h = observation.get('grid_width', 10), observation.get('grid_height', 10)
    obstacles = set(map(tuple, observation.get('obstacles', [])))
    resources = list(map(tuple, observation.get('resources', [])))
    opp = observation.get('opponent_position', [])
    ox, oy = opp[0], opp[1]

    def safe(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prioritize resource collection if resources are available
    resource_positions = resources
    if resource_positions:
        min_d, target = min((dist((x, y), r), r) for r in resource_positions)
        dx = (target[0] > x) - (target[0] < x)
        dy = (target[1] > y) - (target[1] < y)
        nx, ny = x + dx, y + dy
        if safe(nx, ny):
            return [dx, dy]
        # Attempt alternative directions to reach resource
        for ddx, ddy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx_alt, ny_alt = x + ddx, y + ddy
            if safe(nx_alt, ny_alt):
                return [ddx, ddy]

    # If no resources, pursue opponent
    dx = (ox > x) - (ox < x)
    dy = (oy > y) - (oy < y)
    nx, ny = x + dx, y + dy
    if safe(nx, ny):
        return [dx, dy]
    # Fallback: move to any safe neighbor
    for ddx, ddy in [(1,0), (-1,0), (0,1), (0,-1)]:
        nx, ny = x + ddx, y + ddy
        if safe(nx, ny):
            return [ddx, ddy]
    return [0, 0]
