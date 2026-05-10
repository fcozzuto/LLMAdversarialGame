def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    oppx, oppy = ox, oy

    candidates = []
    for x, y in unclaimed:
        if inside(x, y) and (x, y) not in opp_terr:
            d = abs(x - sx) + abs(y - sy)
            danger = abs(x - oppx) + abs(y - oppy)
            candidates.append((d, -danger, x, y))
    if candidates:
        candidates.sort()
        tx, ty = candidates[0][2], candidates[0][3]
    else:
        # fallback: stay in/near self territory, avoid opponent
        tx, ty = sx, sy
        best = None
        for x, y in self_terr or [(sx, sy)]:
            if inside(x, y):
                val = -(abs(x - oppx) + abs(y - oppy))
                if best is None or val > best:
                    best = val
                    tx, ty = x, y

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        to_opp = abs(nx - oppx) + abs(ny - oppy)
        score = (dist, -to_opp, abs(dx) + abs(dy))
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]