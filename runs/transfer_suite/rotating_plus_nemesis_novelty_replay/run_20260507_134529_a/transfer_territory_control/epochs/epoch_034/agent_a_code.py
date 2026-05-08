def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")
    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh_dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cell_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        s = 0
        if (nx, ny) in opp_terr:
            s += 1000
        elif (nx, ny) in self_terr:
            s += 10
        elif (nx, ny) in unclaimed:
            s += 6
            adj_un = 0
            adj_opp = 0
            for dx, dy in neigh_dirs:
                ax, ay = nx + dx, ny + dy
                if inb(ax, ay):
                    if (ax, ay) in unclaimed:
                        adj_un += 1
                    elif (ax, ay) in opp_terr:
                        adj_opp += 1
            s += 2 * adj_un + 5 * adj_opp
        else:
            s += 1
        # Prefer moving toward opponent territory (but don't chase blindly when blocked).
        d_opp = abs(nx - ox) + abs(ny - oy)
        s += max(0, 40 - d_opp) * 0.5
        # Slight preference to reduce distance to the closest opponent-owned cell.
        if opp_terr:
            md = min(abs(nx - px) + abs(ny - py) for (px, py) in opp_terr)
            s += max(0, 20 - md)
        return s

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best = None
    best_s = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        s = cell_score(nx, ny)
        if s > best_s:
            best_s = s
            best = [dx, dy]
    return best if best is not None else [0, 0]