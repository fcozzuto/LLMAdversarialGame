def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles if len(p) >= 2)
    if (sx, sy) in obs:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    res = [(r[0], r[1]) for r in resources if len(r) >= 2 and inb(r[0], r[1]) and (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Value = prioritize being closer than opponent, then closeness to that resource,
        # and also reward immediate pickup by landing on a resource.
        best_here = None
        for rx, ry in res:
            dself = dist(nx, ny, rx, ry)
            dopp = dist(ox, oy, rx, ry)
            advantage = dopp - dself  # positive means we're closer
            pickup = 1000 if (nx == rx and ny == ry) else 0
            # If opponent is closer, still move to the resource that minimizes how bad it is.
            val = pickup + 50 * advantage - dself - (0.1 * dopp)
            if best_here is None or val > best_here:
                best_here = val

        # Tie-break deterministically: higher value, then smaller dx/dy lexicographically.
        key = (best_here, -abs(dx) - abs(dy), -dx, -dy)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]