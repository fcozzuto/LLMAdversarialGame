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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Limit search to keep deterministic/fast: only consider nearby unclaimed targets.
    nearby_unclaimed = []
    for (ux, uy) in unclaimed:
        if abs(ux - sx) + abs(uy - sy) <= 6 or abs(ux - ox) + abs(uy - oy) <= 6:
            nearby_unclaimed.append((ux, uy))
    if not nearby_unclaimed:
        nearby_unclaimed = list(unclaimed)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        man_to_opp = abs(nx - ox) + abs(ny - oy)
        val += -man_to_opp  # general pressure

        if (nx, ny) in resources:
            val += 10
        if (nx, ny) in unclaimed:
            val += 6
        if (nx, ny) in opp_terr:
            val += 24 - min(8, man_to_opp)

        # Intercept counter-claim: prefer moves that put us closer than opponent to many unclaimed cells.
        for (ux, uy) in nearby_unclaimed:
            if (ux, uy) in obstacles:
                continue
            d_me = abs(ux - nx) + abs(uy - ny)
            d_opp = abs(ux - ox) + abs(uy - oy)
            if d_me == d_opp:
                continue
            if d_me < d_opp:
                advantage = d_opp - d_me
                if advantage >= 1:
                    # Also favor targets near our current area
                    local = abs(ux - sx) + abs(uy - sy)
                    val += 3 + min(6, advantage) - min(4, local // 3)

        # Prefer staying connected with our territory (reduce flipping waste).
        if (nx, ny) in self_terr:
            val += 2

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]