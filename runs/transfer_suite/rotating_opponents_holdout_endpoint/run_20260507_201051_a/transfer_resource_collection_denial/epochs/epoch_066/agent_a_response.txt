def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        dx = 0 if sx == ox else (1 if ox > sx else -1)
        dy = 0 if sy == oy else (1 if oy > sy else -1)
        return [dx, dy]

    # Select a resource we can reach sooner than the opponent (or deny with closest race).
    best = None
    for tx, ty in resources:
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        # Prefer winning race; if tied, prefer far advantage for us.
        key = (do - ds, -min(ds, do), ds, tx, ty)
        if best is None or key > best[0]:
            best = (key, (tx, ty))
    _, (tx, ty) = best

    # If already on the best resource, try to keep collecting nearby (stay otherwise).
    if (sx, sy) == (tx, ty):
        # Deterministically move toward opponent-competition: reduce distance to nearest resource.
        # (Still deterministic, avoids stalling when other resources exist.)
        nearest = min(resources, key=lambda r: (man(sx, sy, r[0], r[1]), r[0], r[1]))
        tx, ty = nearest

    # Choose move that best improves our race vs target while not stepping into obstacles.
    cur_ds = man(sx, sy, tx, ty)
    cur_do = man(ox, oy, tx, ty)
    best_m = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = man(nx, ny, tx, ty)
        # Opponent not moved this turn; use current position as deterministic proxy.
        # Score: maximize (opponent gap improvement), then minimize our distance, then prefer diagonal.
        score = ((cur_do - ns) - (cur_do - cur_ds), -ns, -(dx != 0 and dy != 0), -abs(dx) - abs(dy), nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]