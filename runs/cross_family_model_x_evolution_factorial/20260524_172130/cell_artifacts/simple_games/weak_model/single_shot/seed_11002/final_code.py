def choose_move(observation):
    px, py = observation['self_position']
    wx, wy = observation['opponent_position']
    obstacles = set(tuple(pos) for pos in observation['obstacles'])
    resources = observation['resources']
    width, height = observation['grid_width'], observation['grid_height']

    def safe(x, y):
        return 0 <= x < width and 0 <= y < height and (x, y) not in obstacles

    # Prioritize moving toward closest resource if any remain
    if resources:
        rx, ry = min(resources, key=lambda r: abs(r[0]-px)+abs(r[1]-py))
        dx, dy = 0, 0
        if rx > px: dx = 1
        elif rx < px: dx = -1
        elif ry > py: dy = 1
        elif ry < py: dy = -1
        if safe(px+dx, py+dy):
            return [dx, dy]
    # Else, move away from opponent if close
    dist_opponent = abs(wx - px) + abs(wy - py)
    if dist_opponent <= 2:
        options = []
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = px+dx, py+dy
            if safe(nx, ny):
                options.append((nx, ny))
        # Move to the furthest point from opponent
        if options:
            options.sort(key=lambda c: - (abs(c[0]-wx)+abs(c[1]-wy)))
            nx, ny = options[0]
            return [nx - px, ny - py]
    # Move randomly or stay
    for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
        nx, ny = px+dx, py+dy
        if safe(nx, ny):
            return [dx, dy]
    return [0,0]
