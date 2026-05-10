def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    unclaimed = observation.get("unclaimed_cells") or []
    uset = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}

    obstacles = observation.get("obstacles") or []
    oset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    opp_terr = observation.get("opponent_territory") or []
    opset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    targets = list(uset) if uset else (list(opset) if opset else [(ox, oy)])
    if not targets:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-(10**18), 0, 0)

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            continue
        is_un = (nx, ny) in uset
        is_opp = (nx, ny) in opset

        # Prefer reaching unclaimed, otherwise contest opponent, while pulling toward center.
        d_target = 10**9
        for tx, ty in targets:
            d = man(nx, ny, tx, ty)
            if d < d_target:
                d_target = d

        d_center = abs(nx - cx) + abs(ny - cy)
        d_from_opp = man(nx, ny, ox, oy)

        score = 0
        score += 3.0 * is_un
        score += 2.2 * is_opp
        score += -0.35 * d_target
        score += -0.12 * d_center
        score += -0.02 * d_from_opp

        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]