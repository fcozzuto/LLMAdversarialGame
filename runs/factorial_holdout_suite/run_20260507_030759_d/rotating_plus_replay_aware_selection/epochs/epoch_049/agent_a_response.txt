def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obst = observation.get("obstacles") or []
    obstacles = set()
    for p in obst:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if not resources or w <= 0 or h <= 0:
        return [0, 0]

    def step_toward(px, py, tx, ty):
        dx = 0 if tx == px else (1 if tx > px else -1)
        dy = 0 if ty == py else (1 if ty > py else -1)
        candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
        for cdx, cdy in candidates:
            nx, ny = px + cdx, py + cdy
            if inb(nx, ny):
                return nx, ny
        return px, py

    best = (-(10**9), 10**9)
    best_mv = (0, 0)

    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        best_for_move = (-(10**9), 10**9)
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            our_d = abs(nsx - rx) + abs(nsy - ry)
            if our_d == 0:
                cand = (10**9, 0)
            else:
                nosx, nosy = ox, oy
                pnx, pny = step_toward(nosx, nosy, rx, ry)
                opp_d_next = abs(pnx - rx) + abs(pny - ry)
                # Maximize advantage against opponent's likely next move; tiebreak by shorter own distance.
                adv = (opp_d_next - our_d)
                cand = (adv * 1000 - our_d, our_d)
            if cand > best_for_move:
                best_for_move = cand

        if best_for_move > best:
            best = best_for_move
            best_mv = (mdx, mdy)

    return [int(best_mv[0]), int(best_mv[1])]