def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        # With diagonal moves, true shortest is Chebyshev; obstacles may block but ok as heuristic.
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        return dx if dx > dy else dy

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = []
    for r in resources:
        rx, ry = r[0], r[1]
        if inb(rx, ry) and (rx, ry) not in obs:
            res.append((rx, ry))
    if not res:
        return [0, 0]

    # Anti-deny: prefer resources we can reach no later than opponent; if none, go toward the resource
    # where we are "least behind" while also reducing opponent's lead after our move.
    scored_resources = []
    for rx, ry in res:
        d_self = dist(sx, sy, rx, ry)
        d_op = dist(ox, oy, rx, ry)
        margin = d_op - d_self  # positive => ahead
        scored_resources.append((margin, d_self, rx, ry))
    scored_resources.sort(reverse=True)  # best margins first

    top = scored_resources[: min(4, len(scored_resources))]

    best = None
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Take up to 3 candidate resources; emphasize being ahead, then being fast.
        val = 0
        for i, (margin0, d_self0, rx, ry) in enumerate(top):
            d_self1 = dist(nx, ny, rx, ry)
            d_op1 = dist(ox, oy, rx, ry)
            margin1 = d_op1 - d_self1
            # Strongly reward turning an equal/behind situation into ahead, and penalize falling further behind.
            val += (margin1 * 500) - (d_self1 * (20 + 5 * i))
            # If we are currently ahead, protect it by not drifting too much from the target.
            val += (margin0 > 0) * max(0, margin0 - margin1) * (-30)
        # Small tie-break toward closer to board center to avoid dead ends when behind on all resources.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        val -= (dist(nx, ny, cx, cy) * 2)
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]