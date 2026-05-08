def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Find a simple deterministic target: nearest opponent territory cell, else nearest unclaimed.
    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = None
    if opp_terr:
        best = None
        for px, py in opp_terr:
            d = manh(px, py, sx, sy)
            if best is None or d < best[0] or (d == best[0] and (px, py) < best[1]):
                best = (d, (px, py))
        target = best[1]
    elif unclaimed:
        best = None
        for px, py in unclaimed:
            d = manh(px, py, sx, sy)
            if best is None or d < best[0] or (d == best[0] and (px, py) < best[1]):
                best = (d, (px, py))
        target = best[1]
    else:
        target = (ox, oy)

    tx, ty = target

    # Score proxy for candidate next cell.
    # Prefer flipping opponent territory, then unclaimed, then pushing toward opponent.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_terr:
            base = 1000
        elif (nx, ny) in unclaimed:
            base = 300
        elif (nx, ny) in self_terr:
            base = 80
        else:
            base = 20

        dist_to_target = manh(nx, ny, tx, ty)
        dist_to_opp = manh(nx, ny, ox, oy)

        # Tie-break deterministically by move ordering.
        score = base - dist_to_target - 0.25 * dist_to_opp
        key = (score, -base, dist_to_target, dist_to_opp, dx, dy)

        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]