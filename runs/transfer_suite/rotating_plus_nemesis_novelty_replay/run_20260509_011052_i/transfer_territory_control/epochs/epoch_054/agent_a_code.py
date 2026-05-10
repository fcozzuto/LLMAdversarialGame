def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def neigh(x, y):
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    def nearest_dist_to_set(x, y, S):
        if not S:
            return 10**9
        best = 10**9
        for px, py in S:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    # Build "frontier" unclaimed cells near opponent territory/pos to contest edges
    frontier = set()
    if opp_terr:
        for tx, ty in opp_terr:
            for nx, ny in neigh(tx, ty):
                if (nx, ny) in unclaimed:
                    frontier.add((nx, ny))
    else:
        for nx, ny in neigh(ox, oy):
            if (nx, ny) in unclaimed:
                frontier.add((nx, ny))

    # Also consider any unclaimed to avoid stalling
    target_pool = frontier if frontier else unclaimed

    best = (-10**18, 0, 0)
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        gain = 0.0
        gain += 1.2 if (nx, ny) in unclaimed else 0.0
        if (nx, ny) in self_terr:
            gain += 0.15

        # Prefer expanding into self-connected regions
        sc = 0
        oc = 0
        for ax, ay in neigh(nx, ny):
            if (ax, ay) in self_terr:
                sc += 1
            if (ax, ay) in opp_terr:
                oc += 1
        gain += 0.25 * sc

        # Avoid getting adjacent to opponent when not capturing
        gain -= 0.35 * oc
        if (nx, ny) in opp_terr:
            gain += 2.2  # flipping on entry is enabled; decisive captures matter

        # Drive towards contested frontier/unclaimed
        dtarget = nearest_dist_to_set(nx, ny, target_pool)
        gain -= 0.08 * dtarget

        # Keep some pressure towards opponent position if frontier is empty
        if not frontier:
            dopp = abs(nx - ox) + abs(ny - oy)
            gain -= 0.03 * dopp

        # Deterministic tie-break
        tie = (0.0, -dx, -dy)  # prefer smaller dx/dy magnitude patterns deterministically
        key = (gain + 1e-9 * tie[0], tie[1], tie[2])
        if key[0] > best[0]:
            best = (key[0], dx, dy)

    return [int(best[1]), int(best[2])]