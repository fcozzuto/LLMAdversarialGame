def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    if not resources:
        if 0 <= sx <= w - 1 and 0 <= sy <= h - 1 and (sx, sy) not in obstacles:
            return [0, 0]
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    # Pick best resource: prefer closer than opponent; else closest by our distance with tie-break.
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        score = (0 if our_d < opp_d else 1, our_d, -opp_d, rx, ry)
        if best is None or score < best[0]:
            best = (score, (rx, ry))
    tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = cheb(nx, ny, tx, ty)
            # Tie-break deterministically by dx,dy ordering.
            cand = (d, dx, dy)
            if best_move is None or cand < best_move:
                best_move = cand
    if best_move is None:
        return [0, 0]
    return [best_move[1], best_move[2]]