def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in (observation.get("self_territory") or []):
        self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in (observation.get("opponent_territory") or []):
        opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = [(int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or [])]
    unclaimed_set = set(unclaimed)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            x, y = sx + dx, sy + dy
            if (dx, dy) == (0, 0) or (0 <= x < w and 0 <= y < h and (x, y) not in obstacles):
                moves.append((dx, dy, x, y))

    if unclaimed:
        targets = unclaimed
    else:
        targets = list(opp_terr) if opp_terr else [(ox, oy)]

    def mindist(p):
        px, py = p
        best = 10**9
        for tx, ty in targets:
            d = abs(tx - px) + abs(ty - py)
            if d < best:
                best = d
        return best

    best_move = (0, 0, sx, sy)
    best_val = -10**18

    for dx, dy, x, y in moves:
        if (x, y) in obstacles:
            continue
        base = 0
        if (x, y) in self_terr:
            base = 0.8
        elif (x, y) in opp_terr:
            base = 2.2  # entering opponent territory flips control
        elif (x, y) in unclaimed_set or (x, y) not in self_terr:
            base = 1.4   # claim unclaimed / contested

        opp_close = abs(x - ox) + abs(y - oy)
        defense = 0.15 * opp_close  # prefer staying farther to reduce easy counters
        approach = -0.25 * mindist((x, y))  # expansion pressure

        val = base + defense + approach
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = (dx, dy, x, y)

    return [int(best_move[0]), int(best_move[1])]