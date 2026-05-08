def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a target resource where we are closer (or at least not far behind opponent).
    best_target = None
    best_key = None
    for rx, ry in res:
        d_s = md(sx, sy, rx, ry)
        d_o = md(ox, oy, rx, ry)
        # Prefer immediate grabs; otherwise maximize advantage against denier.
        # Key sorts: higher advantage, then smaller self distance, then deterministic position.
        adv = d_o - d_s
        key = (-d_s, -adv, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    # If blocked (resource on obstacle), just move away deterministically.
    if (sx, sy) in obs:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    # Greedy one-step towards target with obstacle avoidance.
    best_step = (0, 0)
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0
        d = md(nx, ny, tx, ty)
        # Also consider opponent distance improvement to deny further.
        d_o_next = md(ox + (1 if ox < nx else (-1 if ox > nx else 0)), oy + (1 if oy < ny else (-1 if oy > ny else 0)), tx, ty)
        # Deterministic ordering: closer first, then maximize (opponent - self) at next, then prefer non-stay.
        key = (d, -(d_o_next - d), dx == 0 and dy == 0, nx, ny)
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]