def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    self_territory = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    self_set = set((int(p[0]), int(p[1])) for p in self_territory if isinstance(p, (list, tuple)) and len(p) == 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) == 2)
    un_set = set((int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) == 2)
    ox, oy = observation["opponent_position"]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh_dirs = dirs

    def adj_to_self(x, y):
        for dx, dy in neigh_dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in self_set:
                return 1
        return 0

    best = None
    best_sc = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        sd = man(nx, ny, sx, sy)
        od = man(nx, ny, ox, oy)
        edge = 1 if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1) else 0

        cell_bonus = 0
        if (nx, ny) in un_set:
            cell_bonus += 1.5
        if (nx, ny) in opp_set:
            cell_bonus += 2.0
        if (nx, ny) in self_set:
            cell_bonus += 0.4

        sc = (od - sd) + cell_bonus + 1.0 * adj_to_self(nx, ny) - 0.3 * edge
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]