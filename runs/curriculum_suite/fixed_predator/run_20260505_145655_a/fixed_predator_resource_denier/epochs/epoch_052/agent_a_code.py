def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target resource to "deny": maximize (opp closer advantage) while keeping us reasonably near.
    best_t = None
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        denial = od - sd
        center_bias = -(((rx - cx) * (rx - cx)) + ((ry - cy) * (ry - cy))) * 1e-4
        # Prefer resources where we can catch up and where opponent is farther.
        tscore = denial * 7.0 - sd + center_bias
        if best_t is None or tscore > best_t[0]:
            best_t = (tscore, rx, ry)

    _, tx, ty = best_t

    # Evaluate immediate move to improve our denial to the target.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # If outside or into obstacle, engine keeps us; reflect that by using current position in scoring.
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        sd = dist(nx, ny, tx, ty)
        od = dist(ox, oy, tx, ty)
        # Strong denial term; small push to reduce distance and avoid drift.
        denial = od - sd
        drift = (nx - tx) * 0.0 + (ny - ty) * 0.0
        score = denial * 9.0 - sd + drift
        # Tie-break deterministically: prefer diagonal then straight then stay.
        pref = (dx == 0) + (dy == 0) + (dx == 0 and dy == 0)
        cand = (score, -pref, dx, dy)
        if best_m is None or cand > best_m:
            best_m = cand

    return [int(best_m[2]), int(best_m[3])]