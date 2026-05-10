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

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Opponent pressure: prefer moves that reduce distance to opponent, but only if controllable.
    opp_dist = md(sx, sy, px, py)
    best = (0, 0)
    best_val = -10**18

    # For a local frontier bias: if an unclaimed cell is adjacent to our territory,
    # heading toward it tends to expand safely.
    frontier = set()
    for (x, y) in self_terr:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed and free(nx, ny):
                frontier.add((nx, ny))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0

        # Base desirability by cell status
        if (nx, ny) in unclaimed:
            val += 220
            # Encourage unclaimed closer to opponent and closer to frontier expansion
            val += (opp_dist - md(nx, ny, px, py)) * 2
            if (nx, ny) in frontier:
                val += 120
            # Avoid overly wandering: slight preference for nearer to us
            val += max(0, 10 - md(nx, ny, sx, sy)) * 3
        elif (nx, ny) in self_terr:
            val += 18
        elif (nx, ny) in opp_terr:
            # Flipping on entry is enabled: counterclaiming is valuable
            val += 140
            val += (opp_dist - md(nx, ny, px, py)) * 4
        else:
            # neutral but don't collide with obstacle: modest preference to move toward center-ish
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            distc = abs(nx - cx) + abs(ny - cy)
            val += -distc * 0.5

        # Tactical: reduce maximum distance (king distance) to opponent
        king_prev = max(abs(sx - px), abs(sy - py))
        king_new = max(abs(nx - px), abs(ny - py))
        val += (king_prev - king_new) * 10

        # Keep some inertia: staying still unless it loses points
        if dx == 0 and dy == 0:
            val -= 3

        # Tie-break deterministically: prefer moves with greater val, then smaller dx, then smaller dy
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]