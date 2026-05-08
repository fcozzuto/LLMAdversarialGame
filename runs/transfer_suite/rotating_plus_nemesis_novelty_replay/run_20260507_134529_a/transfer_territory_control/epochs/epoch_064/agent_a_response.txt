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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best = None
    best_score = -10**18

    # Prefer decisive territorial flips at the edge: move into opponent territory when possible.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            score = -1000
        else:
            score = 0.0
            if (nx, ny) in opp_terr:
                score += 6.0
            if (nx, ny) in unclaimed:
                score += 3.5
            if (nx, ny) in self_terr:
                score += 1.0
            if (nx, ny) in resources:
                score += 0.8

            # Distance shaping: if we can flip soon, approach opponent; otherwise stay safer.
            d_to_opp = abs(nx - ox) + abs(ny - oy)
            score += (-0.15 * d_to_opp)

            # Avoid stepping into "easy capture" by opponent: prefer squares with fewer adjacent opponent cells.
            adj_opp = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    tx, ty = nx + ax, ny + ay
                    if inb(tx, ty) and (tx, ty) in opp_terr:
                        adj_opp += 1
            score += (-0.7 * adj_opp)

            # Light bias to keep expanding outward from our current territory.
            if self_terr:
                min_self = min(abs(nx - fx) + abs(ny - fy) for fx, fy in self_terr)
                score += (-0.05 * min_self)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]