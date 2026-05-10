def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []

    obset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    ucell = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}
    uset = {(p[0], p[1]) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    oset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def neigh8(x, y):
        return [(x+dx, y+dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]

    # If any unclaimed exist, use nearest to bias (deterministic).
    nearest_u = None
    best_du = 10**9
    if ucell:
        for (x, y) in ucell:
            d = man(ax, ay, x, y)
            if d < best_du or (d == best_du and (x < nearest_u[0] or y < nearest_u[1])):
                best_du = d
                nearest_u = (x, y)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obset:
            continue

        is_opp = (nx, ny) in oset
        is_un = (nx, ny) in ucell
        adj_opp = 0
        adj_ob = 0
        for (px, py) in neigh8(nx, ny):
            if (px, py) in oset:
                adj_opp += 1
            if (px, py) in obset:
                adj_ob += 1

        bias = 0
        if nearest_u is not None:
            bias = -0.12 * man(nx, ny, nearest_u[0], nearest_u[1])
        # Favor flipping opponent territory / edging into it; otherwise claim unclaimed.
        val = 0
        val += 18.0 if is_opp else 0.0
        val += 7.0 if is_un else 0.0
        val += 2.0 * adj_opp
        val += -0.8 * adj_ob
        val += bias
        # Slightly discourage running into our own territory corner when equal (deterministic tie-break).
        if (nx, ny) in uset:
            val += -0.15

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]