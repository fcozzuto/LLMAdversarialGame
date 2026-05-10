def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    self_terr = set(tuple(map(int, p)) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(map(int, p)) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(map(int, p)) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(map(int, p)) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if opp_terr:
        cx = sum(x for x, _ in opp_terr) / max(1, len(opp_terr))
        cy = sum(y for _, y in opp_terr) / max(1, len(opp_terr))
    else:
        cx, cy = ox, oy

    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def adj_unclaimed(x, y):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed:
                c += 1
        return c

    def adj_opp(x, y):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in opp_terr:
                c += 1
        return c

    def obstacle_adj(x, y):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                c += 1
        return c

    def center_dist2(x, y):
        dx = x - cx
        dy = y - cy
        return dx * dx + dy * dy

    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = 0.0
        in_u = (nx, ny) in unclaimed
        in_o = (nx, ny) in opp_terr
        in_s = (nx, ny) in self_terr
        if in_u:
            sc += 7.0
        if in_o:
            sc += 4.5
        if in_s:
            sc += 1.0

        sc += 2.2 * adj_unclaimed(nx, ny)
        sc -= 2.0 * adj_opp(nx, ny)
        sc -= 1.1 * obstacle_adj(nx, ny)

        # Bias away from opponent center-claim; still allow close captures.
        sc += 0.12 * center_dist2(nx, ny) - 0.08 * center_dist2(sx, sy)
        man_to_opp = abs(nx - ox) + abs(ny - oy)
        sc += (1.5 if in_o else 0.0) - 0.05 * man_to_opp

        # Deterministic tie-break: prefer not staying still unless equally good.
        sc += (0.01 if (dx != 0 or dy != 0) else -0.01)

        if sc > best_sc or (sc == best_sc and (best is None or (dx, dy) < best)):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]