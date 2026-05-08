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

    # Opponent "center" for deterministic distance pressure.
    if opp_terr:
        c = sorted(opp_terr)
        ax = sum(p[0] for p in c) / len(c)
        ay = sum(p[1] for p in c) / len(c)
    else:
        ax, ay = ox, oy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort()

    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        # Prefer claiming/raiding while keeping safe-ish from opponent pressure.
        base = 0
        if cell in resources:
            base += 3
        if cell in unclaimed:
            base += 4
        if cell in self_terr:
            base += 1
        if cell in opp_terr:
            base += 2  # flipping on entry is enabled

        # Penalize moving closer to opponent centroid; reward distance.
        dist_opp_pos = abs(nx - ox) + abs(ny - oy)
        dist_opp_center = abs(nx - ax) + abs(ny - ay)
        safety = (dist_opp_center + 0.5 * dist_opp_pos)

        # Mild preference to expand away from our own corner if early; else hold.
        corner_bias = (nx + ny) if (sx <= w // 2 and sy <= h // 2) else ((w - 1 - nx) + (h - 1 - ny))

        v = base * 10 + safety - 0.05 * corner_bias
        if best is None or v > bestv:
            bestv = v
            best = [dx, dy]

    return best if best is not None else [0, 0]