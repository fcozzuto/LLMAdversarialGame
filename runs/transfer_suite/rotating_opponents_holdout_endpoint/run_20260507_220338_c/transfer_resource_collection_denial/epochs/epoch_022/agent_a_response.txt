def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (0, 1), (1, 0), (0, -1),
             (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate this next position against all resources: maximize "can arrive first"
        local_best = None
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            # If we step onto a resource, heavily prioritize it
            pick = 1 if (nx, ny) == (rx, ry) else 0
            advantage = opd - myd
            key = (pick, advantage, -myd, -rx, -ry)
            if local_best is None or key > local_best:
                local_best = key

        if local_best is None:
            continue
        # Prefer the move that best secures the earliest collection over all resources
        if best_key is None or local_best > best_key:
            best_key = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]