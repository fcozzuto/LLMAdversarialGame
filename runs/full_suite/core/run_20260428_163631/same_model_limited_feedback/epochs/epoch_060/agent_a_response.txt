def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def clamp(px, py):
        if px < 0: px = 0
        elif px >= w: px = w - 1
        if py < 0: py = 0
        elif py >= h: py = h - 1
        return px, py

    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_set.add((p[0], p[1]))

    move_options = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = clamp(x + dx, y + dy)
            move_options.append((dx, dy, nx, ny))

    # If we are on a resource, prefer to stay this turn (deterministic).
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2 and r[0] == x and r[1] == y:
            return [0, 0]

    # Choose a target resource we can reach earlier than the opponent.
    def cheb(a, b, c, d):
        da = a - c
        db = b - d
        if da < 0: da = -da
        if db < 0: db = -db
        return da if da > db else db

    best_res = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if (rx, ry) in obs_set:
            continue
        ds = cheb(x, y, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Offensive/dominance: smaller (ds - 0.9*do). Tie-break: smaller ds.
        key = (ds - 0.9 * do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    # If no resources, drift toward opponent's side to contest.
    if best_res is None:
        tx, ty = (w - 1, h - 1) if (x < w - 2 or y < h - 2) else (0, 0)
    else:
        tx, ty = best_res

    # Score candidate moves: prefer ones that reduce distance to target, avoid obstacles, and hinder opponent.
    best_move = None
    best_score = None
    for dx, dy, nx, ny in move_options:
        if (nx, ny) in obs_set:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Also discourage moving toward the opponent too much (keeps us in resource races).
        score = (d_self, -0.05 * d_opp)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        # All blocked: allow staying (or first bounded move) deterministically.
        return [0, 0]

    return [int(best_move[0]), int(best_move[1])]