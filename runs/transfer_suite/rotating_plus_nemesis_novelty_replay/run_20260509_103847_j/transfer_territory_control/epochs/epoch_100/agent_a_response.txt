def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    self_tr = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_tr.add((int(p[0]), int(p[1])))
    opp_tr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_tr.add((int(p[0]), int(p[1])))
    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))
    cx, cy = w // 2, h // 2
    cur = (sx, sy)

    perimeter = set()
    for (x, y) in self_tr:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and (nx, ny) not in self_tr:
                perimeter.add((nx, ny))
    if not perimeter:
        perimeter = set(unclaimed) if unclaimed else {(cx, cy)}

    def neigh_count(t, x, y):
        c = 0
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in t:
                c += 1
        return c

    best = (10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        target = (nx, ny)
        if target in opp_tr:
            base = -50  # aggressive flip
        elif target in unclaimed or target in perimeter:
            base = -10  # expansion
        elif target in self_tr:
            base = 0  # staying/defending
        else:
            base = 5  # fallback
        opp_adj = neigh_count(opp_tr, nx, ny)
        self_adj = neigh_count(self_tr, nx, ny)
        # prefer moves that increase our adjacency to frontier while reducing opp adjacency
        frontier_gain = -2 * (1 if target in unclaimed or target in perimeter else 0) - 2 * self_adj + 2 * opp_adj
        center_bias = abs(nx - cx) + abs(ny - cy)
        # deterministic tie-breaker: prefer smallest dx,dy lexicographically after score
        score = (base + frontier_gain + center_bias, abs(dx), abs(dy))
        if score < (best[0], best[1], best[2]):
            best = (score[0], dx, dy)
    return [int(best[1]), int(best[2])]