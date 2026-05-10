def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_pos = tuple(observation["opponent_position"])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def local_counts(cell):
        x, y = cell
        uc = ot = st = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            if (nx, ny) in unclaimed: uc += 1
            if (nx, ny) in opp_terr: ot += 1
            if (nx, ny) in self_terr: st += 1
        return uc, ot, st

    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        cell = (nx, ny)

        uc, ot, st = local_counts(cell)
        base = 0.0
        if cell in unclaimed: base += 6.0
        if cell in self_terr: base += 1.5
        if cell in opp_terr:
            base -= 4.0
            # only willingly enter opponent territory if it opens unclaimed nearby
            base += 2.5 if uc >= 2 else 0.0

        # encourage expanding toward unclaimed and away from being swallowed
        base += 0.9 * uc
        base += 0.2 * st
        base += 0.35 * (1 if ot == 0 else 0)

        # detour slightly based on opponent distance to intercept less, and expand more
        base += 0.15 * dist(cell, opp_pos)  # prefer farther (safer expansion)
        base -= 0.05 * dist((sx, sy), opp_pos) * (0 if dx == 0 and dy == 0 else 1)

        # avoid oscillation on empty tiles
        base -= 0.5 if cell not in unclaimed and cell not in self_terr and cell not in opp_terr else 0.0

        # tie-break deterministically toward moves with larger progress
        prog = abs(dx) + abs(dy)
        cand = (base, prog, -dist(cell, (sx, sy)))
        if cand > best:
            best = cand
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]