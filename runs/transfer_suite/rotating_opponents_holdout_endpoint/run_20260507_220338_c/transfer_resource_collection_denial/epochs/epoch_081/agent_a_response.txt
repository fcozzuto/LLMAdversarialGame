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

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx >= dy else dy

    # Pick target that maximizes our advantage in arrival time; if none, pick best "greedy" target.
    best = None
    best_key = None
    for t in res:
        sd = dist((sx, sy), t)
        od = dist((ox, oy), t)
        adv = od - sd  # positive means we arrive earlier
        key = (adv, -sd, t[0], t[1])  # deterministic tie breaks
        if best_key is None or key > best_key:
            best_key = key
            best = t

    tx, ty = best
    options = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                options.append((dx, dy))

    # Prefer moves that reduce distance to target; if multiple, prefer maximizing opponent distance decrease.
    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        before_sd = dist((sx, sy), (tx, ty))
        after_sd = dist((nx, ny), (tx, ty))
        gain_self = before_sd - after_sd
        before_od = dist((ox, oy), (tx, ty))
        after_od = dist((ox, oy), (tx, ty))  # opponent doesn't move now; keep deterministic bias via our position
        # extra tie-break: move that gets us closer to target and farther from opponent
        self_to_opp = dist((nx, ny), (ox, oy))
        return (gain_self, self_to_opp, -abs(tx - nx), -abs(ty - ny), dx, dy)

    best_move = None
    best_mkey = None
    for dx, dy in options:
        k = score_move(dx, dy)
        if best_mkey is None or k > best_mkey:
            best_mkey = k
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]