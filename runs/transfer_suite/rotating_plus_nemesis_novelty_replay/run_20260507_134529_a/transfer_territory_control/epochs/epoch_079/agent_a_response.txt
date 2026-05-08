def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_val = -1e18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy
        if not cell_ok(nx, ny):
            return [0, 0]

        if (nx, ny) in opp_terr:
            base = 6.0
        elif (nx, ny) in unclaimed:
            base = 2.2
        elif (nx, ny) in self_terr:
            base = 0.6
        else:
            base = 0.2

        if (nx, ny) in resources:
            base += 1.2

        adj_opp = 0
        adj_un = 0
        adj_self = 0
        for ax, ay in neigh:
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                if (tx, ty) in opp_terr:
                    adj_opp += 1
                elif (tx, ty) in unclaimed:
                    adj_un += 1
                elif (tx, ty) in self_terr:
                    adj_self += 1

        # Push the frontier: prioritize moves that touch opponent territory/unclaimed.
        frontier = 0.55 * adj_opp + 0.25 * adj_un - 0.12 * adj_self

        # Keep pressure: small reward for reducing distance to opponent.
        d_now = abs(sx - ox) + abs(sy - oy)
        d_next = abs(nx - ox) + abs(ny - oy)
        pressure = 0.08 * (d_now - d_next)

        val = base + frontier + pressure

        if val > best_val + 1e-9:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best