def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)

    obstacles_raw = observation.get("obstacles") or []
    obstacles = {(p[0], p[1]) for p in obstacles_raw if p is not None and len(p) >= 2}

    unclaimed_raw = observation.get("unclaimed_cells") or []
    unclaimed = {(p[0], p[1]) for p in unclaimed_raw if p is not None and len(p) >= 2}

    oppx, oppy = observation.get("opponent_position", (w - 1, h - 1))

    def md(x, y, tx, ty):
        return abs(x - tx) + abs(y - ty)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    behind = False
    try:
        myc = observation.get("self_territory_count", None)
        opc = observation.get("opponent_territory_count", None)
        if myc is not None and opc is not None:
            behind = myc < opc
    except Exception:
        behind = False

    tx, ty = oppx, oppy
    if unclaimed:
        best = None
        bd = 10**9
        for p in unclaimed:
            d = md(sx, sy, p[0], p[1])
            if d < bd or (d == bd and (p[0], p[1]) < best):
                bd = d
                best = p
        tx, ty = best

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dtarget = md(nx, ny, tx, ty)
        score = -dtarget

        if (nx, ny) in unclaimed:
            score += 5 if not behind else 7

        # Avoid moving onto/adjacent to opponent when not behind
        dadj = md(nx, ny, oppx, oppy)
        if dadj == 0:
            score -= 100
        else:
            score -= (3 if not behind else 1) * (1 if dadj == 1 else 0)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]