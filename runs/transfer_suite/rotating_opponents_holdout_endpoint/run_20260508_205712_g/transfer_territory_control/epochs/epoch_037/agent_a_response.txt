def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def is_opp_frontier_cell(x, y):
        if (x, y) not in unclaimed:
            return False
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in opp_terr:
                return True
        return False

    # Find a target: unclaimed adjacent to opponent territory, else nearest unclaimed/opp.
    frontier_targets = []
    if unclaimed and opp_terr:
        for (x, y) in unclaimed:
            if is_opp_frontier_cell(x, y):
                frontier_targets.append((x, y))
        if not frontier_targets:
            frontier_targets = list(unclaimed)[:]

    if frontier_targets:
        tx, ty = min(frontier_targets, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), abs(c[0] - ox) + abs(c[1] - oy)))
    else:
        candidates = list(unclaimed) if unclaimed else []
        if not candidates:
            tx, ty = ox, oy
        else:
            tx, ty = min(candidates, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy)))

    best = None
    best_sc = -10**18
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            sc = -10**12
        else:
            sc = 0
            if (nx, ny) in opp_terr:
                sc += 5000
            elif (nx, ny) in unclaimed:
                sc += 120
            if (nx, ny) in self_terr:
                sc -= 20
            # Prefer moving closer to target
            sc += 2 * (-(abs(nx - tx) + abs(ny - ty)))
            # Slightly prefer disrupting near opponent frontier
            if unclaimed and is_opp_frontier_cell(nx, ny):
                sc += 250
            # Avoid stagnation: prefer not staying unless no better move
            if dx == 0 and dy == 0:
                sc -= 5
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]