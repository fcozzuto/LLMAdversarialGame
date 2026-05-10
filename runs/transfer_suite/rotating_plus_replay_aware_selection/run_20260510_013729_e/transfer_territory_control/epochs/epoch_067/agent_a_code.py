def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_set = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_set.add((int(p[0]), int(p[1])))

    opp_set = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_set.add((int(p[0]), int(p[1])))

    unclaimed = []
    uc = observation.get("unclaimed_cells")
    if isinstance(uc, list):
        for p in uc:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if (x, y) not in self_set and (x, y) not in opp_set:
                    unclaimed.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cand = []
    if unclaimed:
        targets = unclaimed
    else:
        r = 3
        targets = []
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                x, y = sx + dx, sy + dy
                if inb(x, y) and (x, y) not in self_set and (x, y) not in opp_set and (x, y) not in obstacles:
                    targets.append((x, y))
    for x, y in targets:
        if (x, y) in obstacles or not inb(x, y):
            continue
        cand.append((man(sx, sy, x, y), -man(ox, oy, x, y), x, y))
    if not cand:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    return [dx, dy]
        return [0, 0]

    cand.sort()
    tx, ty = cand[0][2], cand[0][3]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                score = man(nx, ny, tx, ty) * 10 + man(nx, ny, ox, oy)
                moves.append((score, dx, dy))
    if moves:
        moves.sort()
        return [int(moves[0][1]), int(moves[0][2])]
    return [0, 0]