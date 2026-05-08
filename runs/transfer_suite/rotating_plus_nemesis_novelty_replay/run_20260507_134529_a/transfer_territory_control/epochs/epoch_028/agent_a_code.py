def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        S = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    S.add((x, y))
        return S

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    cand_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = None
    if unclaimed:
        best = None
        best_val = -10**18
        for x, y in sorted(unclaimed):
            ds = abs(sx - x) + abs(sy - y)
            do = abs(ox - x) + abs(oy - y)
            val = (do * 2) - ds
            if val > best_val:
                best_val = val
                best = (x, y)
        target = best
    elif opp_terr:
        best = None
        best_val = 10**18
        for x, y in sorted(opp_terr):
            val = md((sx, sy), (x, y))
            if val < best_val:
                best_val = val
                best = (x, y)
        target = best
    else:
        target = (ox, oy)

    if target is None:
        return [0, 0]

    tx, ty = target
    best_move = (0, 0)
    best_dist = 10**18
    best_do = -1

    for dx, dy in cand_moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = abs(nx - tx) + abs(ny - ty)
        do = abs(nx - ox) + abs(ny - oy)
        if d < best_dist or (d == best_dist and do > best_do):
            best_dist = d
            best_do = do
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]