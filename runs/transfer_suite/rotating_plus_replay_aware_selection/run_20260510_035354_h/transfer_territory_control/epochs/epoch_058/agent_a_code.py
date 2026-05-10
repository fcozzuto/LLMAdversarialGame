def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            targets.append((p[0], p[1]))
    if not targets:
        res = observation.get("resources") or []
        for p in res:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.append((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if targets:
            d = min(man(nx, ny, tx, ty) for (tx, ty) in targets)
        else:
            d = man(nx, ny, ox, oy)
        d_opp = man(nx, ny, ox, oy)
        sc = (-d) + 0.2 * d_opp
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]