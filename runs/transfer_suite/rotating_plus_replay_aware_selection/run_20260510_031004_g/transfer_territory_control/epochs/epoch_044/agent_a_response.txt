def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cheb = lambda a, b, c, d: max(abs(a - c), abs(b - d))
    manh = lambda a, b, c, d: abs(a - c) + abs(b - d)
    cur_d = cheb(sx, sy, px, py)

    best = (0, 0)
    best_val = -10**18
    # Pick a nearby focus unclaimed cell if possible (deterministic).
    focus = None
    if unclaimed:
        focus = min(unclaimed, key=lambda t: (manh(sx, sy, t[0], t[1]), cheb(sx, sy, px, py), t[0], t[1]))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 420
            if focus is not None:
                val += 35 - 5 * manh(nx, ny, focus[0], focus[1])
        if (nx, ny) in self_terr:
            val += 30
        if (nx, ny) in opp_terr:
            val += 160  # flipping on entry
            if cheb(nx, ny, px, py) == 1:
                val -= 55  # opponent can likely contest immediately

        # Safety: avoid stepping into positions too close to opponent unless it flips.
        dnew = cheb(nx, ny, px, py)
        val += 10 * (dnew - cur_d)  # move away helps

        if dnew == 1:
            val -= 45
            if (nx, ny) in opp_terr:
                val += 25  # still good to flip even if adjacent

        # Prefer reducing distance to any unclaimed cell if focus wasn't set.
        if focus is None and unclaimed:
            # deterministic approximate: use minimal distance to unclaimed
            md = min(manh(nx, ny, ux, uy) for ux, uy in unclaimed)
            val += 20 - 4 * md

        # Tie-break deterministically.
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]