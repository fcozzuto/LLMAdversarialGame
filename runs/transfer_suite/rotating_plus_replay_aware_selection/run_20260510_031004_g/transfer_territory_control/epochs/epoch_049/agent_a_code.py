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

    # Mode switch to change behavior deterministically (helps avoid being stuck).
    self_cnt = int(observation.get("self_territory_count", len(self_terr)))
    opp_cnt = int(observation.get("opponent_territory_count", len(opp_terr)))
    turn = int(observation.get("turn_index", 0))
    ahead = self_cnt - opp_cnt
    sweep_mode = (ahead < 5) or (turn % 3 == 1)  # if behind or in a periodic window: push harder

    # Targeting bias
    tx, ty = (px, py) if sweep_mode else (w - 1 - px, h - 1 - py)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Quick frontier preference: choose cells that reduce distance to our goal and don't allow immediate opponent gain.
    best = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0
        d_goal = max(1, man(nx, ny, tx, ty))
        val += 80 // d_goal  # closer to goal is better

        if (nx, ny) in unclaimed:
            val += 420  # strong claim
            val += 20 // max(1, man(nx, ny, sx, sy))
        if (nx, ny) in self_terr:
            val += 25  # keep territory
        if (nx, ny) in opp_terr:
            # flipping on entry is powerful; reward it heavily
            val += 700

        # Voronoi-ish: prefer cells that are closer to us than to opponent
        ds = man(nx, ny, sx, sy)
        dp = man(nx, ny, px, py)
        val += 120 * (1 if ds <= dp else -1)

        # Avoid walking into "easy flips": if we move adjacent to opponent while behind, it can backfire.
        adj_opp = (max(abs(nx - px), abs(ny - py)) == 1)
        if adj_opp:
            if ahead >= 0:
                val += 30  # we're strong: adjacency can mean grabbing
            else:
                val -= 120  # we're weaker: don't feed flips

        # Obstacle-adjacent mild penalty (reduces chances of invalid moves later)
        if any((nx + ox, ny + oy) in obstacles for (ox, oy) in [(-1, 0), (1, 0), (0, -1), (0, 1)]):
            val -= 8

        # Small deterministic tie-breaker: prefer moves that reduce distance to opponent when sweeping, else away.
        if sweep_mode:
            val += (-(man(nx, ny, px, py)))
        else:
            val += (man(nx, ny, px, py))

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]