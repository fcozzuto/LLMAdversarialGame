def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def to_set(lst):
        s = set()
        for p in lst or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obst = to_set(observation.get("obstacles"))
    selfT = to_set(observation.get("self_territory"))
    oppT = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_unclaimed(x, y):
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax or ay:
                    if (x + ax, y + ay) in unclaimed:
                        return 1
        return 0

    def dist_to(targets, x, y):
        best = 10**9
        for tx, ty in targets:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
        return best if best < 10**9 else 0

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        if (nx, ny) in selfT:
            base = 1
        elif (nx, ny) in oppT:
            base = 25
        elif (nx, ny) in unclaimed:
            base = 18
        else:
            base = 5

        center_bias = -(abs(nx - cx) + abs(ny - cy)) * 0.5
        unclaimed_bonus = adj_unclaimed(nx, ny) * 9

        opp_target = list(oppT)
        unclaimed_target = list(unclaimed)
        # Prefer expansion early; contest when ahead/centered or when unclaimed is sparse.
        ahead = int(observation.get("self_territory_count", 0) > observation.get("opponent_territory_count", 0))
        unclaimed_sparse = 1 if len(unclaimed_target) < (w * h) // 4 else 0
        prefer_opp = 1 if (ahead or unclaimed_sparse) and len(opp_target) else 0

        if prefer_opp:
            cont = -dist_to(opp_target, nx, ny) * 1.2
        else:
            cont = -dist_to(unclaimed_target, nx, ny) * 1.0

        score = base + unclaimed_bonus + center_bias + cont
        # Deterministic tie-break: prefer straighter moves then up-left priority order already fixed by neigh.
        candidates.append((score, -abs(dx) - abs(dy) * 0.01, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [int(candidates[0][2]), int(candidates[0][3])]