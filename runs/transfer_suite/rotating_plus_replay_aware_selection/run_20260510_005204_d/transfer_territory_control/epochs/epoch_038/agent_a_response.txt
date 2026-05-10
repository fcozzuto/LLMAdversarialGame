def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_unclaimed(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def centroid(terr):
        if not terr:
            return (w / 2.0, h / 2.0)
        xs = 0.0
        ys = 0.0
        n = 0
        for x, y in terr:
            xs += x
            ys += y
            n += 1
        return (xs / n, ys / n)

    ocx, ocy = centroid(opp_terr)
    cendx, cendy = (w - 1) / 2.0, (h - 1) / 2.0
    opp_count = len(opp_terr)

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = 0
        if (nx, ny) in opp_terr:
            v += 130 - 3 * opp_count
        elif (nx, ny) in unclaimed:
            v += 70
        elif (nx, ny) in self_terr:
            v += 5
        else:
            v += 0
        v += 10 * adj_unclaimed(nx, ny)

        # Pressure: if opponent controls many cells, steer towards their centroid.
        # Otherwise, expand towards center while keeping distance from opponent.
        dist_opp = abs(nx - ocx) + abs(ny - ocy)
        dist_cen = abs(nx - cendx) + abs(ny - cendy)
        if opp_count >= 10:
            v -= 1.2 * dist_opp
            v -= 0.05 * dist_cen
        else:
            v += 0.08 * (14 - dist_cen) - 0.02 * dist_opp

        # Deterministic tie-break: prefer diagonal first, then lexicographic.
        key = (-v, (0 if (dx != 0 and dy != 0) else 1), dy, dx)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best