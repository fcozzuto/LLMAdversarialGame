def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Choose move by prioritizing resources where we gain distance lead,
    # while strongly avoiding competing on the opponent's current row (sweep_rows behavior).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            nx, ny = sx, sy
        val = 0
        for tx, ty in res:
            myd = md(nx, ny, tx, ty)
            opd = md(ox, oy, tx, ty)
            # Lead: prefer where opponent is farther than we are.
            lead = opd - myd
            # Anti-competition: deprioritize same-row as opponent (likely sweep lane).
            row_factor = -6 if ty == oy else 3
            # Small tie-break: prefer nearer to reduce time-to-capture.
            urgency = -0.3 * myd
            # Mild preference to not linger: reward movement that decreases our distance to some resource.
            val += (lead * 5) + row_factor + urgency
        # Normalize by count of resources to keep scale stable.
        val //= max(1, len(res))
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]