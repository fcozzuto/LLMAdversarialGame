def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []

    uset = {(p[0], p[1]) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    oset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    ucell = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}
    obset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    opp_dist = man(ax, ay, ox, oy)
    targets = list(ucell) if ucell else (list(oset) if oset else [])
    nearest_target = None
    if targets:
        bestd = 10**9
        for tx, ty in targets:
            d = man(ax, ay, tx, ty)
            if d < bestd:
                bestd = d
                nearest_target = (tx, ty)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obset:
            continue

        val = 0
        if (nx, ny) in oset:
            val += 800  # immediate capture pressure
        if (nx, ny) in uset:
            val += 30   # keep territory
        if (nx, ny) in ucell:
            val += 120  # claim new cells

        if nearest_target is not None:
            val -= 3 * man(nx, ny, nearest_target[0], nearest_target[1])

        val -= 2 * man(nx, ny, ox, oy)  # avoid drifting too close unless capturing
        if opp_dist > 0:
            val += 1 if man(nx, ny, ox, oy) < opp_dist else 0  # slight incentive to approach when useful

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]