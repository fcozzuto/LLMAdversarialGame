def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    def norm_pos(p):
        try:
            x, y = p
            return int(x), int(y)
        except Exception:
            return None

    sp = norm_pos(observation.get("self_position"))
    op = norm_pos(observation.get("opponent_position"))
    if sp is None or op is None:
        return [0, 0]
    sx, sy = sp
    ox, oy = op

    obstacles = set()
    for o in observation.get("obstacles") or []:
        q = norm_pos(o)
        if q is not None:
            obstacles.add(q)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    role = (observation.get("self_role") or "pursuer").lower()
    is_evader = role == "evader"

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def greedy_pursuer(from_pos, target_pos):
        fx, fy = from_pos
        tx, ty = target_pos
        best = None
        best_d = None
        for dx, dy in moves:
            nx, ny = fx + dx, fy + dy
            if not ok(nx, ny):
                continue
            d = dist((nx, ny), (tx, ty))
            if best is None or d < best_d or (d == best_d and (dx, dy) < best):
                best, best_d = (dx, dy), d
        return best if best is not None else (0, 0)

    best_move = (0, 0)
    if not is_evader:
        # Pursuer: one-step greedy to minimize distance (with obstacle-aware tie-break).
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            man = dist((nx, ny), (ox, oy))
            # small preference to move (avoid standing unless tied)
            score = (-man, 0 if (dx == 0 and dy == 0) else -0.01, (nx, ny))
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        # Evader: predict opponent greedy response (assume pursuer) and maximize resulting distance.
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            opp_dx, opp_dy = greedy_pursuer((ox, oy), (nx, ny))
            nox, noy = ox + opp_dx, oy + opp_dy
            if not ok(nox, noy):
                nox, noy = ox, oy
            d2 = dist((nx, ny), (nox, noy))
            corner_bonus = (nx in (0, w - 1) and ny in (0, h - 1)) - 0.0  # deterministic, prefers corners slightly
            stay_pen = 0 if (dx != 0 or dy != 0) else -0.02
            score = (d2 + corner_bonus + stay_pen, -(abs(dx) + abs(dy)), (nx, ny))
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]