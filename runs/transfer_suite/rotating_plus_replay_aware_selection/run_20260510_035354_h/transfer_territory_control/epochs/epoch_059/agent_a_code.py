def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []
    opp_terr = observation.get("opponent_territory") or []

    uset = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}
    oset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    opset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}

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

    def nearest_dist(pt, sset, fallback=None):
        if not sset:
            return fallback if fallback is not None else 10**9
        x, y = pt
        best = 10**9
        for tx, ty in sset:
            d = man(x, y, tx, ty)
            if d < best:
                best = d
        return best

    targets = uset
    if not targets:
        targets = opset if opset else {(ox, oy)}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            continue

        d_to_un = nearest_dist((nx, ny), targets, fallback=10**9)
        d_to_opp = man(nx, ny, ox, oy)
        d_to_opp_terr = nearest_dist((nx, ny), opset, fallback=d_to_opp if targets is uset else 10**9)
        enter_opp = (nx, ny) in opset

        val = 0
        val += -2.2 * d_to_un
        val += 0.35 * d_to_opp
        val += 0.6 * (d_to_opp_terr if d_to_opp_terr < 10**9 else 0)
        if enter_opp:
            val += 6.0  # flipping on entry; take shallow counter-capture if we step on their cells

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]