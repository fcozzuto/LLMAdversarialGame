def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj(a, bset):
        x, y = a
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in bset:
                        return True
        return False

    def min_dist_to_opp(cell):
        x, y = cell
        if not opp_t:
            return 10**9
        best = 10**9
        for ox, oy in opp_t:
            d = abs(ox - x) + abs(oy - y)
            if d < best:
                best = d
        return best

    self_zone_extend = adj((sx, sy), self_t) or True
    best = (0, 0)
    best_sc = -10**18

    # Targets: prefer unclaimed cells that are far from opponent (avoid flipping into enemy), but reachable.
    targets = list(unclaimed)
    if not targets:
        targets = list(self_t)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        nxt = (nx, ny)

        # Heuristic components
        sc = 0

        # Prefer expanding into unclaimed; slight bonus for stepping into our frontier.
        if nxt in unclaimed:
            sc += 8
        if (not nxt in self_t) and adj(nxt, self_t):
            sc += 3

        # Strongly discourage stepping directly into opponent territory unless it also increases separation.
        if nxt in opp_t:
            sc -= 20

        # Encourage moving away from opponent territory to control more cells safely.
        d_opp = min_dist_to_opp(nxt)
        sc += min(10, d_opp) * 1.2

        # Small bias for progressing toward "good" unclaimed cells: far-from-opp but within local area.
        if targets:
            best_t = None
            best_md = 10**9
            for tx, ty in targets:
                if abs(tx - nx) > 2 or abs(ty - ny) > 2:
                    continue
                md = abs(tx - nx) + abs(ty - ny)
                if md < best_md:
                    best_md = md
                    best_t = (tx, ty)
            if best_t:
                sc += 2.5 / (1 + best_md)
                # If that target is far from opponent, bias more.
                if opp_t:
                    t_opp_d = min(abs(ox - best_t[0]) + abs(oy - best_t[1]) for ox, oy in opp_t)
                    sc += min(6, t_opp_d) * 0.6

        # Avoid getting stuck adjacent to opponent (local duel zone)
        if adj(nxt, opp_t):
            sc -= 6

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [best[0], best[1]]