def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if (sx, sy) in resources:
        return [0, 0]

    if not resources:
        for dx, dy in [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    my = (sx, sy)
    opp = (ox, oy)

    best = None
    for tx, ty in resources:
        self_d = dist(my, (tx, ty))
        opp_d = dist(opp, (tx, ty))
        # Prefer resources we can beat: smaller (self_d - opp_d), then smaller self_d, then deterministic coords
        key = (self_d - opp_d, self_d, tx, ty)
        if best is None or key < best[0]:
            best = (key, (tx, ty))
    _, target = best
    tx, ty = target

    # Choose a legal neighbor that greedily reduces self distance to target;
    # secondary: also increases distance from opponent.
    best_move = (None, None)  # (key, (dx,dy))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        self_d = dist((nx, ny), (tx, ty))
        opp_d = dist((nx, ny), opp)
        # minimize self_d, maximize opp_d; deterministic tie on move
        key = (self_d, -opp_d, dx, dy)
        if best_move[0] is None or key < best_move[0]:
            best_move = (key, (dx, dy))

    if best_move[1] is None:
        return [0, 0]
    dx, dy = best_move[1]
    return [int(dx), int(dy)]