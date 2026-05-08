def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    st = set(map(tuple, observation.get("self_territory") or []))
    ot = set(map(tuple, observation.get("opponent_territory") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neigh4(x, y):
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                yield nx, ny

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = 0
        if (nx, ny) in unclaimed:
            v += 60
        if (nx, ny) in ot:
            v += 55  # flipping on entry
        if (nx, ny) in st:
            v += 5

        # Prefer moving towards center, but primarily expand/steal near opponent boundary.
        distc = abs(nx - cx) + abs(ny - cy)
        v += int(20 - 2.5 * distc)

        # Boundary leverage: entering unclaimed next to opponent territory is strong.
        adj_opp = 0
        for ax, ay in neigh4(nx, ny):
            if (ax, ay) in ot:
                adj_opp += 1
        if (nx, ny) in unclaimed:
            v += 18 * adj_opp
        else:
            v += 8 * adj_opp

        # Avoid stepping into likely dead zones: if surrounded by obstacles/edges, lower value.
        block = 0
        for tx, ty in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1)):
            if not ok(tx, ty):
                block += 1
        v -= 3 * block

        # Tie-break deterministically: prefer larger x then y.
        v = v * 100 + (nx * 2 + ny)

        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best