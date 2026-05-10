def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def pick_target():
        targets = unclaimed[:]
        if not targets:
            if opp_t:
                targets = list(opp_t)
            else:
                targets = [(sx, sy)]
        best = None
        for tx, ty in targets:
            d = abs(tx - sx) + abs(ty - sy)
            dc = abs(tx - cx) + abs(ty - cy)
            do = abs(tx - ox) + abs(ty - oy)
            score = (d, dc, -do, ty, tx)
            if best is None or score < best[0]:
                best = (score, (tx, ty))
        return best[1]

    tx, ty = pick_target()

    # If we're already on/inside the opponent's territory, bias toward pushing outward from it.
    pushing = (sx, sy) in opp_t

    def move_score(nx, ny):
        if (nx, ny) in obstacles:
            return (10**9, 10**9, 10**9, 10**9)
        # Favor capturing new/contested area; slightly avoid obstacles and opponent proximity unless pushing.
        in_self = (nx, ny) in self_t
        in_opp = (nx, ny) in opp_t
        un = (nx, ny) in unclaimed
        d_to_target = man((nx, ny), (tx, ty))
        d_center = abs(nx - cx) + abs(ny - cy)
        d_to_opp = man((nx, ny), (ox, oy))
        # Base priorities: approach target, keep center, then avoid opponent if not pushing.
        base = (d_to_target, d_center, (d_to_opp if not pushing else -d_to_opp), 0 if (in_opp or un) else 1)
        # If pushing, prioritize entering opponent cells; otherwise prioritize unclaimed.
        bonus = 0 if pushing else 0
        if pushing:
            bonus = 0 if in_opp else 1
        else:
            bonus = 0 if un else (0 if not in_self else 2)
        return (base[0], base[1], base[2], bonus)

    best_move = (0, 0)
    best_s = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        s = move_score(nx, ny)
        if best_s is None or s < best_s:
            best_s = s
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]