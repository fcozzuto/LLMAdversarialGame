def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []
    opp_terr = observation.get("opponent_territory") or []
    self_terr = observation.get("self_territory") or []
    self_terr_set = set(map(tuple, self_terr))
    opp_terr_set = set(map(tuple, opp_terr))
    unclaimed_set = set(map(tuple, unclaimed))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax + ay

    if unclaimed:
        targets = list(unclaimed)
    elif resources:
        targets = list(resources)
    elif opp_terr:
        targets = list(opp_terr)
    else:
        targets = [(w - 1, h - 1)]

    # Deterministic target choice: closest, then lowest y, then lowest x
    bx, by = targets[0][0], targets[0][1]
    best = manhattan(sx, sy, bx, by)
    for tx, ty in targets:
        d = manhattan(sx, sy, tx, ty)
        if d < best or (d == best and (ty < by or (ty == by and tx < bx))):
            best = d
            bx, by = tx, ty

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = manhattan(nx, ny, bx, by)
        # Prefer entering unclaimed, then opponent territory, then anything else; avoid just orbiting
        bonus = 0
        if (nx, ny) in unclaimed_set:
            bonus -= 4
        elif (nx, ny) in opp_terr_set:
            bonus -= 2
        elif (nx, ny) in self_terr_set:
            bonus += 1
        # Small deterministic tie-break
        tie = (ny << 4) + nx
        score = nd + (100 if (dx == 0 and dy == 0) else 0) + bonus + tie * 0.0001
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]