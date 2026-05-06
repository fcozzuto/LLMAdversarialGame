def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obs_list = observation.get("obstacles", []) or []
    obs = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose target with preference for resources we can reach no later than opponent.
    best = None
    target = None
    for r in resources:
        if not isinstance(r, (list, tuple)) or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # First preference: take reachable resources (ds <= do), tie: smaller ds, then position.
        reachable = 0 if ds <= do else 1
        v = (reachable, ds, rx, ry)
        if best is None or v < best:
            best = v
            target = (rx, ry)

    # If opponent is strictly closer to all, "intercept" by moving toward a cell on opponent->target path.
    # Deterministic: align by reducing the larger component first.
    rx, ry = target
    # Candidate interception point (one step closer from our position toward a path point).
    dx = 0 if (rx == sx) else (1 if rx > sx else -1)
    dy = 0 if (ry == sy) else (1 if ry > sy else -1)
    base = (sx + dx, sy + dy) if legal(sx + dx, sy + dy) else (sx, sy)

    # Evaluate best next move with a combined heuristic:
    # - minimize distance to chosen target
    # - and increase distance to opponent (to reduce their ability to contest).
    best_move = [0, 0]
    best_score = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not legal(nx, ny):
            continue
        ds = man(nx, ny, rx, ry)
        dso = man(nx, ny, ox, oy)
        do = man(ox, oy, rx, ry)
        # If we're not competitive (do < ds+1), slightly bias toward moving away from opponent.
        non_comp = 1 if do < ds else 0
        score = (non_comp, ds, -dso, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [mx, my]

    # If all moves blocked, stay put.
    return [int(best_move[0]), int(best_move[1])]