def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p[:2]) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    unclaimed = [tuple(p[:2]) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]
    resources = [tuple(p[:2]) for p in (observation.get("resources") or []) if p and len(p) >= 2]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose a strategic target: close to us, far from opponent (to counter edge-claim behavior).
    candidates = unclaimed if unclaimed else (resources if resources else [])
    if not candidates:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy
    else:
        best = None
        best_key = None
        for x, y in candidates:
            if not inb(x, y):
                continue
            du = dist(sx, sy, x, y)
            do = dist(ox, oy, x, y)
            # Minimize: du - do (prefer far from opponent). Tie-break by du.
            key = (du - do, du, abs(x - (w - 1) // 2) + abs(y - (h - 1) // 2), x, y)
            if best_key is None or key < best_key:
                best_key = key
                best = (x, y)
        tx, ty = best if best is not None else ((w - 1) // 2, (h - 1) // 2)

    # One-step greedy move toward target with obstacle avoidance.
    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    best_step = (0, 0)
    best_score = None
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            # Prefer reducing distance to target; slight preference to increasing distance from opponent.
            d_to = dist(nx, ny, tx, ty)
            d_opp = dist(nx, ny, ox, oy)
            score = (d_to, -(d_opp), abs(dx) + abs(dy))
            if best_score is None or score < best_score:
                best_score = score
                best_step = (dx, dy)
    return [int(best_step[0]), int(best_step[1])]