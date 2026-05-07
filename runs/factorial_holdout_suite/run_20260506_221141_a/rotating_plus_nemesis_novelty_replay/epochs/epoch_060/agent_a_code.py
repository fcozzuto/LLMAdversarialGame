def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obs_set.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs_set:
                resources.append((rx, ry))

    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if sx == cx else (1 if cx > sx else -1)
        dy = 0 if sy == cy else (1 if cy > sy else -1)
        return [dx, dy]

    def dist(a, b, c, d):
        ad = a - c
        if ad < 0: ad = -ad
        bd = b - d
        if bd < 0: bd = -bd
        return ad + bd

    # Pick resource maximizing "we arrive sooner" advantage; break ties by closeness.
    best = None
    for tx, ty in resources:
        sd = dist(sx, sy, tx, ty)
        od = dist(ox, oy, tx, ty)
        # Strongly prefer resources where we can beat the opponent to the pick.
        adv = od - sd
        key = (adv, -sd, tx, ty)
        if best is None or key > best[0]:
            best = (key, tx, ty)
    tx, ty = best[1], best[2]

    # Move selection: deterministic greedy toward target with anti-blocking against obstacles.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        # Prefer reducing our Manhattan distance to target; if tied, prefer increasing opponent distance to target.
        sd2 = dist(nx, ny, tx, ty)
        od2 = dist(ox, oy, tx, ty)
        # slight preference for progressing generally (avoid stalling unless best).
        stall_pen = 1 if (dx == 0 and dy == 0) else 0
        key = (-sd2, (od2 - sd2), -stall_pen, -abs((nx - tx)) - abs((ny - ty)), dx, dy)
        if cand is None or key > cand[0]:
            cand = (key, dx, dy)

    if cand is None:
        # All moves blocked; stay.
        return [0, 0]
    return [cand[1], cand[2]]