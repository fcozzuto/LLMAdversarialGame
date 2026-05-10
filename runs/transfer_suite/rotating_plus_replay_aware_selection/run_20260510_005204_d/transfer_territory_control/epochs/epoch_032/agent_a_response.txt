def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    candidates = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in opp_terr:
                candidates.append((x, y))

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not candidates:
        # If no unclaimed, try to move into opponent-territory adjacent cells, otherwise stay.
        best_move = (0, 0)
        best_score = -10**9
        for dx, dy in moves:
            x, y = sx + dx, sy + dy
            if not inb(x, y):
                continue
            if (x, y) in opp_terr:
                score = 1000 - (abs(x - sx) + abs(y - sy))
            else:
                score = - (abs(x - (w - 1)) + abs(y - (h - 1)))
            if score > best_score:
                best_score, best_move = score, (dx, dy)
        return [best_move[0], best_move[1]]

    def adjacent_to_opp(x, y):
        for nx in (x - 1, x, x + 1):
            for ny in (y - 1, y, y + 1):
                if (nx, ny) in opp_terr:
                    return True
        return False

    # Choose best target deterministically with prioritization.
    best_t = None
    best_key = None
    for x, y in candidates:
        dist = abs(x - sx) + abs(y - sy)
        # Prefer grabbing cells near opponent's border, then those closer.
        pri = 0 if adjacent_to_opp(x, y) else 1
        # Slight bias toward expanding in the direction of opponent corner (opposite of ours).
        corner_bias = (abs((w - 1) - x) + abs((h - 1) - y))
        key = (pri, dist, corner_bias, x, y)
        if best_key is None or key < best_key:
            best_key, best_t = key, (x, y)

    tx, ty = best_t
    best_move = (0, 0)
    best_md = None
    # Deterministic tie-break via move order.
    for dx, dy in moves:
        x, y = sx + dx, sy + dy
        if not inb(x, y):
            continue
        md = abs(tx - x) + abs(ty - y)
        if best_md is None or md < best_md:
            best_md, best_move = md, (dx, dy)
    return [best_move[0], best_move[1]]