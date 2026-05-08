def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    targets = []
    for key in ("unclaimed_cells", "resources", "opponent_territory"):
        if targets:
            break
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.append((int(p[0]), int(p[1])))
        if targets:
            break
    if not targets:
        targets = [(ox, oy), (w // 2, h // 2)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_terr:
            score = -10**12
        else:
            d_self = min(dist((nx, ny), t) for t in targets)
            d_opp = min(dist((nx, ny), t) for t in [(ox, oy)])
            score = -(d_self * 10 + d_opp)
            score += 2 if (nx, ny) == (ox, oy) else 0
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return best