def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)
    res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            res.append((x, y))

    if (sx, sy) in obs or not res:
        return [0, 0]
    if (sx, sy) in res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    move_order = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    blocked = set(obs)

    def obstacle_adj_pen(nx, ny):
        # Stronger penalty for stepping next to obstacles; allows diagonal corridors but avoids hugging walls.
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in blocked:
                    pen += 2
        return pen

    best_move = (0, 0)
    best_val = None
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue

        # Find nearest resource for us and opponent.
        # If we can reach something sooner than opponent, prioritize it.
        min_self = 10**9
        min_opp = 10**9
        min_gap = -10**9
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds < min_self:
                min_self = ds
            if do < min_opp:
                min_opp = do
            gap = do - ds
            if gap > min_gap:
                min_gap = gap

        # Resource attraction: prefer smaller ds (closer to some remaining resource).
        # Opponent pressure: maximize how much earlier we can arrive to some resource.
        val = 0
        val += 8 * min_gap
        val += -min_self
        # Additional tie-breaker: if opponent is far from their nearest resource, slightly prefer this.
        val += max(0, 5 - min_opp) * 0.5
        val -= obstacle_adj_pen(nx, ny) * 1.5

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]