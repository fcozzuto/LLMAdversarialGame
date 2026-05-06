def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Predict opponent next step toward its nearest resource (deterministic tie-break).
    if resources:
        opp_t = min(resources, key=lambda r: (d2(ox, oy, r[0], r[1]), r[0], r[1]))
        tx, ty = opp_t[0], opp_t[1]
        best = None
        bestmv = (0, 0)
        for dx, dy in deltas:
            nx, ny = ox + dx, oy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            key = (d2(nx, ny, tx, ty), dx, dy)
            if best is None or key < best:
                best = key
                bestmv = (dx, dy)
        pred_ox, pred_oy = ox + bestmv[0], oy + bestmv[1]
    else:
        pred_ox, pred_oy = ox, oy

    best_move = (0, 0)
    best_key = None

    # Choose move that (1) improves resource proximity, and (2) contests opponent position.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            best_r = min(resources, key=lambda r: (d2(nx, ny, r[0], r[1]), r[0], r[1]))
            rx, ry = best_r[0], best_r[1]
            r_score = -d2(nx, ny, rx, ry)
        else:
            # Drift to center if no resources, but still contest.
            r_score = -d2(nx, ny, (w - 1) // 2, (h - 1) // 2)

        contest = -d2(nx, ny, pred_ox, pred_oy)
        sep_from_opp = d2(nx, ny, ox, oy)
        # Prefer better contest, but avoid clustering too tightly if it doesn't help.
        key = (
            -r_score,                 # smaller is better
            -contest,                 # smaller is better
            sep_from_opp,             # keep some separation (or tie-break)
            dx, dy                     # deterministic tie-break
        )
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]