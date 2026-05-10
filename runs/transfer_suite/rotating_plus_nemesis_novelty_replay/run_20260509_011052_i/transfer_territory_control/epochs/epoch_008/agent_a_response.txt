def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_count = int(observation.get("opponent_territory_count", len(opp_terr)) or 0)
    self_count = int(observation.get("self_territory_count", len(self_terr)) or 0)

    if observation.get("turn_index", 0) % 10 == 0 and self_count >= opp_count:
        prioritize_attack = False
    else:
        prioritize_attack = opp_count >= self_count

    targets = []
    edge_unclaimed = [c for c in unclaimed if c[0] == 0 or c[0] == w - 1 or c[1] == 0 or c[1] == h - 1]
    if edge_unclaimed:
        targets = edge_unclaimed
    elif unclaimed:
        targets = list(unclaimed)
    elif opp_terr:
        targets = list(opp_terr)
    else:
        targets = list(opp_terr) if opp_terr else []

    def best_dist(x, y, cells):
        if not cells:
            return 999
        md = 10**9
        for cx, cy in cells:
            d = abs(cx - x) + abs(cy - y)
            if d < md:
                md = d
        return md

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        v = 0.0
        if (nx, ny) in opp_terr:
            v += 40.0 + (2.0 if prioritize_attack else 0.0)
        elif (nx, ny) in unclaimed:
            v += 10.0
        elif (nx, ny) in self_terr:
            v += 1.0
        else:
            v -= 1.0

        d_un = best_dist(nx, ny, targets)
        v += (8.0 / (1.0 + d_un))

        # slight center bias to stabilize control
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(nx - cx) + abs(ny - cy)
        v -= 0.03 * dist_center

        # if we're behind, prefer opponent adjacency
        if opp_count > self_count and opp_terr:
            adj = 0
            for ox, oy in opp_terr:
                if abs(ox - nx) <= 1 and abs(oy - ny) <= 1:
                    adj = 1
                    break
            v += 3.0 * adj

        if v > best_val:
            best_val = v
            best = [dx, dy]

    return best if best is not None else [0, 0]