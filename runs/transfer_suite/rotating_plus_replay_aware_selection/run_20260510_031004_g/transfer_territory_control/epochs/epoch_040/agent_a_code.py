def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0))
    early = t < 20

    target = None
    if unclaimed:
        # nearest unclaimed with slight tie-break towards our front (towards opponent corner)
        tx, ty = px, py
        target = min(unclaimed, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), abs(c[0] - tx) + abs(c[1] - ty)))

    best = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0

        if (nx, ny) in self_terr:
            val += 30
        if (nx, ny) in opp_terr:
            val += 140  # flipping on entry
        if (nx, ny) in unclaimed:
            val += 260

        # Voronoi-ish pressure: prefer cells where opponent is farther than us (us distance=0 for candidate)
        d_opp = abs(nx - px) + abs(ny - py)
        val += (d_opp * 3)

        # If early, strongly bias towards nearest unclaimed; later, bias towards opponent territory
        if target is not None and early:
            val += - (abs(nx - target[0]) + abs(ny - target[1])) * 5
        if target is None and early:
            val += - (abs(nx - px) + abs(ny - py)) * 2
        if (not early) and opp_terr:
            # move towards any opponent territory cell: approximate by choosing direction that reduces min manhattan
            # (local proxy: use dx/dy to reduce distance to opponent)
            val += - (abs(nx - px) + abs(ny - py)) * 4 + 10

        # Avoid getting into immediate reach of opponent when not capturing
        if (nx, ny) not in opp_terr and d_opp <= 1:
            val -= 35
        # Prefer expanding towards opponent when adjacent to opponent territory
        if max(abs(nx - px), abs(ny - py)) == 1:
            val += 25

        key = (val, -abs(dx) - abs(dy), dx, dy)
        if key > (best_val, -abs(best[0]) - abs(best[1]), best[0], best[1]):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]