def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_t = None
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        if sd == 0 and od == 0:
            adv = 0
        else:
            adv = od - sd
        center = -(abs(tx - cx) + abs(ty - cy))
        # Deterministic tie-break favors upper-left when scores equal.
        v = (adv, center, -sd, -(tx + 2 * ty))
        if best is None or v > best:
            best, best_t = v, (tx, ty)

    tx, ty = best_t
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = man(nx, ny, tx, ty)
                # Avoid stepping too close to opponent (diagonal probe can contest).
                adj = max(abs(nx - ox), abs(ny - oy))
                opp_pen = 0
                if adj <= 1:
                    opp_pen = 3
                cand.append((d + opp_pen, adj, nx, ny, dx, dy))
    cand.sort()
    return [int(cand[0][4]), int(cand[0][5])]