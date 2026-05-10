def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    sr = (observation.get("self_role", "") or "").lower()
    pr = "pursuer" in sr or "pursue" in sr

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    pref = [(0,-1), (-1,0), (1,0), (0,1), (-1,-1), (1,-1), (-1,1), (1,1), (0,0)]
    ordered = [m for m in pref if m in moves] + [m for m in moves if m not in pref]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def score_candidate(nx, ny):
        d = manhattan(nx, ny, ox, oy)
        adj_pen = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
            ax, ay = nx + dx, ny + dy
            if (ax, ay) in obs_set:
                adj_pen += 1
        corner_bonus = 0
        if (nx in (0, w - 1)) and (ny in (0, h - 1)):
            corner_bonus = 0.5
        base = -d if pr else d
        return base - 0.35 * adj_pen + corner_bonus

    best_move = [0, 0]
    best_val = None
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        val = score_candidate(nx, ny)
        if best_val is None:
            best_val = val
            best_move = [dx, dy]
        else:
            if pr:
                if val > best_val:
                    best_val = val
                    best_move = [dx, dy]
            else:
                if val > best_val:
                    best_val = val
                    best_move = [dx, dy]

    if ok(sx + best_move[0], sy + best_move[1]):
        return best_move
    return [0, 0]