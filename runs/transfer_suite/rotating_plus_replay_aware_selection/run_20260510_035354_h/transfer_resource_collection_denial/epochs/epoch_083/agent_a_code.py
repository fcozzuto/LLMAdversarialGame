def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    opp_role = (observation.get("opponent_role", "") or "").lower()

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Strategic change: incorporate opponent pattern bias (sweep_rows -> avoid their imminent lane,
    # favor targets that keep us ahead even if they are "nearby-sweepable").
    same_row_bias = 0
    if "row" in opp_role:
        same_row_bias = 1

    best = None
    best_key = None
    for rx, ry in res:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        ahead = od - sd
        # If opponent sweeps rows, mildly penalize resources on opponent's current row (likely to be collected first).
        lane_pen = 0
        if same_row_bias and ry == oy:
            lane_pen = -1  # deterministic small penalty
        # Prefer reachable sooner, then deterministic by coordinates.
        key = (ahead + lane_pen, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_delta = [0, 0]
    best_move_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        nd = cheb(nx, ny, tx, ty)
        my_to_opp = cheb(nx, ny, ox, oy)
        # Move towards target; slightly prefer keeping distance from opponent to avoid forced races.
        move_key = (-nd, -my_to_opp, -nx, -ny, dx, dy)
        if best_move_key is None or move_key > best_move_key:
            best_move_key = move_key
            best_delta = [dx, dy]

    return best_delta