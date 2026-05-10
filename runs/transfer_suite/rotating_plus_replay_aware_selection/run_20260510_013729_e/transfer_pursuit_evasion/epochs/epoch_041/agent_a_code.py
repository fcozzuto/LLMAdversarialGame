def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chase" in role) or ("hunter" in role)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def score_cell(x, y):
        if not in_bounds(x, y) or (x, y) in obs:
            return -10**9
        dpo = man(x, y, ox, oy)

        if not obs:
            min_obs = 99
        else:
            min_obs = min(man(x, y, bx, by) for bx, by in obs)

        if is_pursuer:
            # Pursuer: minimize distance, keep away from obstacles, mildly prefer moving toward nearest corner of opponent.
            best_corner = min(corners, key=lambda c: man(c[0], c[1], ox, oy))
            corner_push = -man(x, y, best_corner[0], best_corner[1]) * 0.02
            return (-dpo * 3.0) + (min_obs * 0.15) + corner_push
        else:
            # Evader: maximize distance, avoid obstacles, prefer hiding in farthest corner from pursuer.
            best_corner = max(corners, key=lambda c: man(c[0], c[1], ox, oy))
            corner_hold = man(x, y, best_corner[0], best_corner[1]) * 0.05
            return (dpo * 3.0) + (min_obs * 0.2) + corner_hold

    best_score = -10**18
    best_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny)
        if sc > best_score:
            best_score = sc
            best_moves = [(dx, dy)]
        elif sc == best_score:
            best_moves.append((dx, dy))

    # Deterministic tie-break: prefer staying, then lexicographically smallest.
    best_moves.sort(key=lambda m: (m[0] != 0 or m[1] != 0, m[0], m[1]))
    return [int(best_moves[0][0]), int(best_moves[0][1])]