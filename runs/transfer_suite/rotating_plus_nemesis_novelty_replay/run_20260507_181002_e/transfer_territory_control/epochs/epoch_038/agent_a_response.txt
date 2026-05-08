def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**18

    un_list = list(unclaimed) if unclaimed else []
    if len(un_list) > 24:
        un_list.sort(key=lambda p: (p[0], p[1]))
        un_list = un_list[:24]
    opp_adj = {(ox + dx, oy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy}

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 6
        if (nx, ny) in oppT:
            score += 5
        if (nx, ny) in selfT:
            score += 1
        if (nx, ny) in opp_adj:
            score += 1
        if un_list:
            d = 10**9
            for tx, ty in un_list:
                dd = abs(tx - nx) + abs(ty - ny)
                if dd < d:
                    d = dd
            score += max(0, 6 - d * 0.5)
        score += -0.08 * (abs(nx - ox) + abs(ny - oy))
        key = (score, -dx, -dy)
        if best is None or score > bestv or (score == bestv and key > best):
            bestv = score
            best = key
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move