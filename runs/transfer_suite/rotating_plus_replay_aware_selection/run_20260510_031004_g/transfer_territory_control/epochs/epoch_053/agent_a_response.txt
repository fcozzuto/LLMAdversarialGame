def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    free = lambda x, y: inb(x, y) and (x, y) not in obstacles
    manh = lambda a, b, c, d: abs(a - c) + abs(b - d)
    cheb = lambda a, b, c, d: max(abs(a - c), abs(b - d))

    # If no unclaimed cells exist, just push toward opponent territory while maintaining safety.
    # Otherwise, take unclaimed that are close, prioritizing those that help attack opponent-held frontiers.
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0

        # Territory and unclaimed priorities
        if (nx, ny) in unclaimed:
            val += 320
        if (nx, ny) in opp_terr:
            val += 120  # flipping on entry
        if (nx, ny) in self_terr:
            val += 15

        # Attack if we can flip (entering opponent territory) or approach their frontier.
        d_to_opp = cheb(nx, ny, px, py)
        val += 18 if d_to_opp == 1 else -4 * d_to_opp

        # Prefer reducing distance to the nearest good target.
        if unclaimed:
            # Nearest unclaimed
            t = min(unclaimed, key=lambda p: manh(nx, ny, p[0], p[1]))
            val += 120 - 2 * manh(nx, ny, t[0], t[1])
        else:
            # No unclaimed: chase nearest opponent territory cell
            t = min(opp_terr, default=(px, py), key=lambda p: manh(nx, ny, p[0], p[1]))
            val += 100 - 2 * manh(nx, ny, t[0], t[1])

        # Don't wander into being isolated: keep within some closeness to our territory or opponent.
        if self_terr:
            d_home = min(cheb(nx, ny, tx, ty) for (tx, ty) in self_terr)
            val += 8 if d_home <= 2 else -2 * d_home
        else:
            val += 0

        candidates.append((val, nx, ny, dx, dy))

    # Deterministic tie-breaker: highest val, then lexicographically smallest (dx, dy)
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda z: (-z[0], z[3], z[4]))
    _, nx, ny, dx, dy = candidates[0]
    return [int(dx), int(dy)]