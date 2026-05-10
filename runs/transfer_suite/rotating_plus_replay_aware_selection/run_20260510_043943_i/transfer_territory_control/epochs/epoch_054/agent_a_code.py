def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    opp_cells = set()
    for p in observation.get("opponent_territory", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_cells.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                unclaimed.append((x, y))

    if not unclaimed:
        targets = list(opp_cells) if opp_cells else []
        if not targets:
            targets = [(ox, oy)]
    else:
        targets = unclaimed

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def dist_to_opponent(x, y):
        if not opp_cells:
            return md(x, y, ox, oy)
        best = None
        for cx, cy in opp_cells:
            d = abs(x - cx) + abs(y - cy)
            if best is None or d < best:
                best = d
        return best if best is not None else md(x, y, ox, oy)

    targets.sort(key=lambda t: (md(sx, sy, t[0], t[1]), -dist_to_opponent(t[0], t[1]), t[0], t[1]))
    tx, ty = targets[0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_move = [0, 0]
    best_score = None

    unclaimed_set = set(unclaimed) if unclaimed else set()
    self_territory_set = set()
    for p in observation.get("self_territory", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_territory_set.add((x, y))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_target = md(nx, ny, tx, ty)
        d_from_opp = dist_to_opponent(nx, ny)

        bonus = 0
        if (nx, ny) in opp_cells:
            bonus += 4000
        elif (nx, ny) in unclaimed_set:
            bonus += 1200
        elif (nx, ny) in self_territory_set:
            bonus += 250

        score = bonus * 10_000 - d_to_target * 100 - d_from_opp
        key = (score, -nx, -ny, dx, dy)
        if best_score is None or key > best_score:
            best_score = key
            best_move = [dx, dy]

    return best_move