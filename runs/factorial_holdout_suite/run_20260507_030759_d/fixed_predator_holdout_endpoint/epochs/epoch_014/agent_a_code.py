def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = {(p[0], p[1]) for p in obs_list}

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        # Chebyshev gives good behavior with diagonals
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = dist(nx, ny, tx, ty)
            cand = (d, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]

    # Denier-aware: prefer resources where we can overtake, evaluated over top candidates.
    def move_value(nx, ny):
        scored = []
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            margin = od - sd  # positive means we arrive no later than opponent
            scored.append((margin, -sd, rx, ry))
        scored.sort(reverse=True)  # highest margin first
        top = scored[:3]  # small deterministic lookahead
        # Maximize worst margin among top options; tie-break by being closer to the best margin target.
        worst_margin = min(m[0] for m in top)
        best_sd = -max(m[1] for m in top)
        # If margins all negative, add pressure to pick a tight contest rather than far chase.
        tight_contest = -min(dist(nx, ny, m[2], m[3]) for m in top)
        return (worst_margin, -best_sd, tight_contest)

    best = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        val = move_value(nx, ny)
        cand = (val, dx, dy)
        if best is None or cand > best:
            best = cand
    return [best[1], best[2]]