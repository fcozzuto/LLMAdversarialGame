def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Choose a primary target: nearest resource to us (tie-break by lexicographic).
    if resources:
        target = min(resources, key=lambda r: (md(sx, sy, r[0], r[1]), r[0], r[1]))
    else:
        # No resources: move to center-ish deterministically.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        target = (cx, cy)

    tx, ty = target

    # Predict opponent next step greedily towards target (deterministic).
    best_opp = None
    best_od = None
    for dx, dy in deltas:
        nx, ny = ox + dx, oy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            d = md(nx, ny, tx, ty)
            if best_od is None or d < best_od or (d == best_od and (nx, ny) < best_opp):
                best_od = d
                best_opp = (nx, ny)
    opp_nx, opp_ny = best_opp if best_opp is not None else (ox, oy)

    best = None
    best_score = None
    for dx, dy, nx, ny in legal:
        my_d = md(nx, ny, tx, ty)

        # Hinder: we prefer to be closer to the target than the opponent (or at least not allow us to be behind).
        opp_d_after = md(opp_nx, opp_ny, tx, ty)

        # Micro-penalty for being adjacent to obstacles (avoid dead zones).
        obs_pen = 0
        for ax in (nx-1, nx, nx+1):
            for ay in (ny-1, ny, ny+1):
                if (ax, ay) in obstacles:
                    obs_pen += 1

        # Also slightly avoid moving directly into the opponent if it gives no target progress.
        opp_dist = md(nx, ny, ox, oy)
        collide_pen = 0 if opp_dist >= 2 else (5 - opp_dist)

        # Main score: prioritize reducing our distance to target, and secondarily outpacing opponent.
        score = (-my_d) + (0.35 * opp_d_after) + (-0.8 * obs_pen) + (-0.25 * collide_pen)

        if best_score is None or score > best_score or (score == best_score and (nx, ny) < best):
            best_score = score
            best = (nx, ny, dx, dy)

    return [int(best[2]), int(best[3])]