def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def adj_to_opp(cx, cy):
        for ddx, ddy in neigh4:
            tx, ty = cx + ddx, cy + ddy
            if inb(tx, ty) and (tx, ty) in oppT:
                return True
        return False

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    target = None
    bestd = 10**9
    for ux, uy in unclaimed:
        if adj_to_opp(ux, uy):
            d = man(x, y, ux, uy)
            if d < bestd:
                bestd, target = d, (ux, uy)
    if target is None and unclaimed:
        for ux, uy in unclaimed:
            d = man(x, y, ux, uy)
            if d < bestd:
                bestd, target = d, (ux, uy)
    if target is None:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        target = (cx, cy)

    best_move = (0, 0)
    best_val = -10**18
    tx, ty = target

    for dx, dy in neigh8:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0
        if (nx, ny) in oppT:
            val += 1000
        elif (nx, ny) in unclaimed:
            val += 140
        elif (nx, ny) in selfT:
            val += 20
        if adj_to_opp(nx, ny):
            val += 55
        val -= 2 * man(nx, ny, tx, ty)
        val += (nx - x) * 0 + (ny - y) * 0  # deterministic no-op
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]