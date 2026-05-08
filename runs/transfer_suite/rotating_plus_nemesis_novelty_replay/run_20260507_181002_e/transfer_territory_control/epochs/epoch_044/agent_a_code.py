def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def norm(p):
        if not p or not isinstance(p, (list, tuple)) or len(p) < 2:
            return None
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            return (x, y)
        return None

    resources = set()
    for p in observation.get("resources") or []:
        t = norm(p)
        if t:
            resources.add(t)

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        t = norm(p)
        if t:
            unclaimed.add(t)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        t = norm(p)
        if t:
            obstacles.add(t)

    if not unclaimed and resources:
        unclaimed = set(resources)
    targets = unclaimed if unclaimed else (resources if resources else set([(ox, oy)]))

    late = float(observation.get("turn_index", 0)) > 50
    want_x, want_y = (ox, oy) if late else (sx, sy)
    if targets:
        best = None
        bestv = 10**9
        for tx, ty in targets:
            if (tx, ty) in obstacles:
                continue
            v = abs(tx - sx) + abs(ty - sy)
            if late:
                v = v + 0.5 * (abs(tx - ox) + abs(ty - oy))
            if v < bestv or (v == bestv and ((tx, ty) < best)):
                bestv = v
                best = (tx, ty)
        if best:
            want_x, want_y = best

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if dx == 0 and dy == 0:
            pass
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = abs(want_x - nx) + abs(want_y - ny)
        # Prefer moving toward target; slight preference for reducing distance to opponent when late.
        score = -d
        if late:
            score -= 0.1 * (abs(nx - ox) + abs(ny - oy))
        # Deterministic tie-break: prefer lexicographically smallest move among equal scores.
        if score > best_score or (score == best_score and [dx, dy] < best_move):
            best_score = score
            best_move = [dx, dy]
    return best_move