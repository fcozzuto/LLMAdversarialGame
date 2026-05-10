def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None:
            continue
        x, y = p
        obstacles.add((int(x), int(y)))

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    if not unclaimed and not opp_t:
        return [0, 0]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def min_dist_to_unclaimed(x, y):
        if not unclaimed:
            return 0
        m = 10**9
        # deterministic: iterate sorted for stability
        for ux, uy in sorted(unclaimed):
            d = abs(ux - x) + abs(uy - y)
            if d < m:
                m = d
                if m == 0:
                    break
        return m

    # Prefer moving toward best "front": unclaimed first, otherwise contesting opponent territory.
    opp_targets = opp_t if unclaimed == set() else opp_t

    def min_dist_to_opp(x, y):
        if not opp_targets:
            return 0
        m = 10**9
        for px, py in sorted(opp_targets):
            d = abs(px - x) + abs(py - y)
            if d < m:
                m = d
                if m == 0:
                    break
        return m

    best = None
    best_val = -1e18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        if (nx, ny) in opp_t:
            base = 8.0
        elif (nx, ny) in unclaimed:
            base = 4.5
        elif (nx, ny) in self_t:
            base = 1.2
        else:
            base = 0.4

        d_un = min_dist_to_unclaimed(nx, ny)
        d_op = min_dist_to_opp(nx, ny)

        # local pressure: count unclaimed in immediate neighborhood after move
        local_un = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty) and (tx, ty) in unclaimed:
                local_un += 1

        # If close to opponent territory, bias for counterclaim while still expanding.
        val = base + 0.6 * local_un + (0.35 / (1 + d_un)) + 0.15 * (1 / (1 + d_op))

        # deterministic tie-break: lexicographic on move then value
        if val > best_val + 1e-12:
            best_val = val
            best = (dx, dy)
        elif abs(val - best_val) <= 1e-12 and best is not None:
            if (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]