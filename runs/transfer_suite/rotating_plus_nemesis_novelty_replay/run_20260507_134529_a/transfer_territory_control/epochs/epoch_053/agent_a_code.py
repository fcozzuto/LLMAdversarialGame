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

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not dirs:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_near = list(opp_terr) if opp_terr else [(ox, oy)]
    neigh = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    curr_dist = md((sx, sy), (ox, oy))

    # Deterministic tie-breaking: fixed order by move list; slight turn-based bias to avoid replay similarity.
    bias = (int(observation.get("turn_index", 0)) % 2) * 0.001

    best = None
    best_sc = -10**18
    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            # Engine will reject invalid moves by staying; treat as very poor.
            sc = -10**12
        else:
            gain = 0
            if (nx, ny) in unclaimed:
                gain = 2
            if (nx, ny) in opp_terr:
                gain = 3  # flipping enabled on entry
            if (nx, ny) in resources:
                gain += 1

            # Safety/pressure: avoid stepping into cells controlled by opponent's area in the neighborhood
            min_opp = min(md((nx, ny), p) for p in opp_near) if opp_near else md((nx, ny), (ox, oy))
            adj_opp = 0
            for ddx, ddy in neigh:
                tx, ty = nx + ddx, ny + ddy
                if (tx, ty) in opp_terr:
                    adj_opp += 1
            closer_pen = 0
            if md((nx, ny), (ox, oy)) < curr_dist:
                closer_pen = 2

            # Prefer expanding while keeping distance; also slightly prefer moves that don't return to own dense area.
            dens_pen = 0
            if (nx, ny) in self_terr:
                dens_pen = 0.5

            sc = gain * 10 + (min_opp * 0.8) - (adj_opp * 6) - closer_pen - dens_pen + (i * 0.0001) + bias

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0] if best else 0), int(best[1] if best else 0)]