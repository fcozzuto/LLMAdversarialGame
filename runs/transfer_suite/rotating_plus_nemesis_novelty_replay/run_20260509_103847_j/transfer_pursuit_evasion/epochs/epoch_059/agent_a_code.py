def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = observation.get("obstacles") or []
    obs_set = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    sr = (observation.get("self_role") or "").lower()
    self_evader = ("evader" in sr) or ("evade" in sr) or ("escape" in sr)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    cx, cy = corner

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Deterministic tie-break preference: still, then +x, +y, then diagonals, then negatives
    tb = {(0, 0): 0, (1, 0): 1, (0, 1): 1, (1, 1): 2, (-1, 1): 2, (1, -1): 2, (-1, -1): 2, (-1, 0): 3, (0, -1): 3}

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_opp = dist(nx, ny, ox, oy)
        d_corner = dist(nx, ny, cx, cy)

        # Avoid stepping into cells adjacent to obstacles too aggressively when evading
        adj_obs = 0
        for ax, ay in [(nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1)]:
            if (ax, ay) in obs_set:
                adj_obs += 1

        if self_evader:
            score = (d_opp * 10) + (d_corner * 2) - (adj_obs * 0.75)
            better = (best_score is None) or (score > best_score) or (score == best_score and tb[(dx, dy)] < tb[best])
        else:
            # Pursuer: minimize distance; slightly prefer progress toward opponent and avoid obstacle-adjacent dead ends
            score = (-d_opp * 10) + (-(dist(nx, ny, ox, oy) // 2)) + (-(adj_obs * 0.25))
            better = (best_score is None) or (score > best_score) or (score == best_score and tb[(dx, dy)] < tb[best])

        if better:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]