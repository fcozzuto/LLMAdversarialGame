def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def obs_pen(x, y):
        if (x, y) in obstacles:
            return 10**9
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 1
        return p

    opp_adj = {(ox + dx, oy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)}
    # Pick a resource we can reach not later than opponent; tie-break by smallest "race slack" and low obstacle penalty
    best = None
    best_key = None
    for rx, ry in res:
        my_d = abs(rx - sx) + abs(ry - sy)
        opp_d = abs(rx - ox) + abs(ry - oy)
        race = my_d - opp_d  # <=0 means we are earlier/same
        slack = my_d
        center = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
        # Small bias: discourage grabbing a resource adjacent to opponent (likely to be stolen next)
        opp_risk = 1 if (rx, ry) in opp_adj else 0
        # Obstacle proximity at resource also matters
        key = (race > 0, race, slack, opp_risk, center, obs_pen(rx, ry))
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d = abs(tx - nx) + abs(ty - ny)
            # Mild avoidance of stepping into opponent "pressure"
            opp_press = 0
            if (nx, ny) in opp_adj:
                opp_press = 2
            # Encourage progress toward target and away from obstacles
            score = (d, opp_press, obs_pen(nx, ny), abs(dx) + abs(dy))
            moves.append((score, [dx, dy]))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda z: z[0])
    return moves[0][1]