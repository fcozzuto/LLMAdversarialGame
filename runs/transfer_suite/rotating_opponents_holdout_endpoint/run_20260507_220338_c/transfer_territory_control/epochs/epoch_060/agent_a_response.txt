def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def to_set(lst):
        s = set()
        for p in lst or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    self_terr = to_set(observation.get("self_territory") or [])
    opp_terr = to_set(observation.get("opponent_territory") or [])
    unclaimed = to_set(observation.get("unclaimed_cells") or [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_pos = observation.get("opponent_position") or (w - 1, h - 1)
    tx, ty = int(opp_pos[0]), int(opp_pos[1])

    best = None
    bestv = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        v = 0.0
        if (nx, ny) in opp_terr:
            v += 6.0
        elif (nx, ny) in unclaimed:
            v += 3.0
        elif (nx, ny) in self_terr:
            v += 0.5

        # Prefer pushing toward opponent: closer to opponent position
        v += 0.15 * (-(dist((nx, ny), (tx, ty))))

        # Prefer moves that increase frontier (adjacent to unclaimed or opponent territory)
        neigh = [(nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1),
                 (nx + 1, ny + 1), (nx + 1, ny - 1), (nx - 1, ny + 1), (nx - 1, ny - 1)]
        adj_u = 0
        adj_o = 0
        adj_s = 0
        adj_obs = 0
        for ax, ay in neigh:
            if not inb(ax, ay):
                continue
            if (ax, ay) in obstacles:
                adj_obs += 1
            if (ax, ay) in unclaimed:
                adj_u += 1
            if (ax, ay) in opp_terr:
                adj_o += 1
            if (ax, ay) in self_terr:
                adj_s += 1
        v += 0.35 * adj_u + 0.55 * adj_o + 0.05 * adj_s
        v -= 0.25 * adj_obs

        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best