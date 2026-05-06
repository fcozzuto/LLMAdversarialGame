def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    rem = int(observation.get("remaining_resource_count", len(resources)))
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Candidate moves: 8-neighborhood + stay, in deterministic order
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cell_blocked(x, y):
        return (x, y) in obs

    best_move = [0, 0]
    best_val = None

    # Scoring: prefer getting to a resource sooner than opponent; also add mild dispersion
    # when resources are low (endgame), prioritize closest available.
    endgame = 1 if rem <= 4 else 0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or cell_blocked(nx, ny):
            nx, ny = sx, sy  # engine would reject; keep deterministic
            dx, dy = 0, 0

        # Evaluate best target from this next position
        local_best = None
        for tx, ty in resources:
            if cell_blocked(tx, ty):
                continue
            self_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)

            # Margin: positive means we are closer (or equal) than opponent
            margin = opp_d - self_d

            # Endgame: focus on absolute closeness to any remaining resource
            if endgame:
                val = (margin, -self_d, -((tx + ty) % 8))
            else:
                # Midgame: strongly prefer resources we can beat; if tied, prefer closer and more "central-ish"
                val = (margin, -self_d, -((tx * 3 + ty * 5) % 11))

            if local_best is None or val > local_best:
                local_best = val

        # Prefer safer/meaningful movement: if all values tie, keep smallest dx,dy lexicographically
        if local_best is None:
            local_best = (-10**9, 0, 0)

        # Slight preference to reduce distance to opponent when we already have advantage in margin
        adv = local_best[0]
        opp_adj = -cheb(nx, ny, ox, oy) if adv > 0 else 0
        total = (local_best[0], local_best[1], local_best[2], opp_adj, -(abs(dx) + abs(dy)), -dx, -dy)

        if best_val is None or total > best_val:
            best_val = total
            best_move = [dx, dy]

    return best_move