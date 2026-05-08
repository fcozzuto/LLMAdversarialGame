def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res:
        return [0, 0]

    def dist_cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx >= dy else dy

    best_t = None
    best_key = None

    # Heuristic change: use Chebyshev distance (diagonal-friendly) and avoid ties where opponent can likely arrive first.
    for tx, ty in res:
        self_d = dist_cheb((sx, sy), (tx, ty))
        opp_d = dist_cheb((ox, oy), (tx, ty))
        adv = opp_d - self_d  # positive => we can arrive earlier (or equal but nearer below)
        tie = self_d
        same_line = (tx == ox) or (ty == oy)
        # If opponent is on same row/col with the resource, penalize less advantage to avoid getting swept.
        line_pen = -2 if same_line and adv <= 0 else 0
        key = (adv, -tie, line_pen)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [dx, dy]