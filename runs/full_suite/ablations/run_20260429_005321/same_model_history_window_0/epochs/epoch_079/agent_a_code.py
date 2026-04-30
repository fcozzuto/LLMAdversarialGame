def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    def clamp(nx, ny):
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1
        return nx, ny

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    for dx, dy in deltas:
        nx, ny = clamp(x + dx, y + dy)
        if (nx, ny) in obstacles:
            nx, ny = x, y  # engine will keep us; mimic as staying
            dx, dy = 0, 0

        # Prefer resources where we are closer than opponent, and closer overall.
        val = -dist((nx, ny), (ox, oy)) * 0.01  # mild anti-staring at opponent
        for rx, ry in resources:
            myd = dist((nx, ny), (rx, ry))
            oppd = dist((ox, oy), (rx, ry))
            if myd == 0:
                val += 1000000  # very strong if we can collect immediately
            # advantage term: larger when we are relatively closer
            val += (oppd - myd) * 10 - myd * 1

        # Small penalty for staying still unless it is best
        if dx == 0 and dy == 0:
            val -= 0.2

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]