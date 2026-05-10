def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) and ("purs" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        # pursuer: chase current opponent (obvious), tie-broken by target corner
        tx, ty = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_corner = dist2(nx, ny, tx, ty)
        fn = free_neighbors(nx, ny)

        # Deterministic tie-break: fixed ordering in moves list + explicit score comparison.
        if is_evader:
            # Maximize distance from opponent; prefer freedom; secondarily drift toward far corner.
            score = (d_opp, fn, -d_corner, 0)
        else:
            # Minimize distance to opponent; prefer freedom; secondarily drift (slightly) toward opponent's "near-corner".
            score = (-d_opp, fn, -d_corner, 0)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]