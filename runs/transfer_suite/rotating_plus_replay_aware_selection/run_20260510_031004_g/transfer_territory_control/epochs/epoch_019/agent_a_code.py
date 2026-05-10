def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def score_cell(x, y):
        if not free(x, y):
            return -10**9
        d = abs(x - px) + abs(y - py)
        bonus = 0
        if (x, y) in unclaimed:
            bonus += 100
        if (x, y) in self_terr:
            bonus -= 5
        # Prefer positions closer to unclaimed (either immediate or nearest)
        if unclaimed:
            best = 10**9
            for ux, uy in unclaimed:
                dd = abs(x - ux) + abs(y - uy)
                if dd < best:
                    best = dd
            bonus -= best
        # Prefer not stepping into tiles adjacent to opponent too aggressively
        bonus += min(d, 20) * 0.2
        return bonus

    best = None
    bestv = -10**18

    # If we can capture immediately (adjacent unclaimed), aim for those; else aim for nearest unclaimed by greedy.
    targets = []
    if self_terr and unclaimed:
        for tx, ty in self_terr:
            for dx, dy in dirs:
                nx, ny = tx + dx, ty + dy
                if (nx, ny) in unclaimed and free(nx, ny):
                    targets.append((nx, ny))
    if not targets:
        targets = list(unclaimed)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = score_cell(nx, ny)
        if targets:
            # If stepping onto/near a target is possible, add deterministic preference.
            tbest = 10**9
            for tx, ty in targets[:30]:
                dd = abs(nx - tx) + abs(ny - ty)
                if dd < tbest:
                    tbest = dd
            v -= tbest * 2
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]