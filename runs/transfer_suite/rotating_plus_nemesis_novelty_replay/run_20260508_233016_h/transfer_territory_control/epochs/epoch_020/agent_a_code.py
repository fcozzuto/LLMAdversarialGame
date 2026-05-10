def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj8(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1

    def step_ok(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return sx, sy
        return nx, ny

    def nearest_target(cells, prefer_adj=False):
        if not cells:
            return None
        if prefer_adj:
            # target unclaimed/opp cells that are adjacent to our territory
            frontier = [c for c in cells if any(adj8(c, t) for t in self_terr)]
            if frontier:
                cells = frontier
        return min(cells, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))

    target_unclaimed = nearest_target(unclaimed, prefer_adj=True) or nearest_target(unclaimed, prefer_adj=False)
    # If we can immediately contest near our frontier, prioritize it.
    target_opp = None
    if self_terr and opp_terr:
        opp_front = [c for c in opp_terr if any(adj8(c, t) for t in self_terr)]
        if opp_front:
            target_opp = min(opp_front, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = step_ok(dx, dy)
        cell = (nx, ny)

        if cell in obstacles:
            continue

        val = 0.0
        # direct gains
        if cell in unclaimed:
            val += 4.0
        if cell in self_terr:
            val += 0.2
        if cell in opp_terr:
            # contest: entering opponent territory flips on entry
            val += 3.0

        # frontier shaping
        if cell not in obstacles and any(adj8(cell, t) for t in self_terr):
            val += 1.2

        # chase targets deterministically
        distu = 99
        if target_unclaimed is not None:
            distu = abs(nx - target_unclaimed[0]) + abs(ny - target_unclaimed[1])
            val += (6.0 - 0.6 * distu)
        dispo = 99
        if target_opp is not None:
            dispo = abs(nx - target_opp[0]) + abs(ny - target_opp[1])
            val += (7.0 - 0.7 * dispo) * (1.0 if cell in opp_terr or any(adj8(cell, t) for t in self_terr) else 0.6)

        # avoid stalling near own territory if we have expansion targets
        if dx == 0 and dy == 0 and (target_unclaimed is not None or target_opp is not None):
            val -= 0.8

        # tie-breaker: prefer moves that reduce Manhattan distance to the chosen target(s)
        tie = 0
        if target_opp is not None and cell in opp_terr:
            tie -= 0.1
        if target_unclaimed is not None:
            tie += -0.001 * abs(nx - target_unclaimed[0]) - 0.001 * abs(ny - target_unclaimed[1])
        val += tie

        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]