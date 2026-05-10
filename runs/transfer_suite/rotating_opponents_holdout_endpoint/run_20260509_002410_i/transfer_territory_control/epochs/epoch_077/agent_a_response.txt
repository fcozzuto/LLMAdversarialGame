def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p is not None and len(p) >= 2)
    opp_t = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p is not None and len(p) >= 2)

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))
    use_unclaimed = len(unclaimed) > 0

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        # Prefer flipping opponent territory when adjacent.
        if (nx, ny) in opp_t:
            val += 100000
        # Prefer taking unclaimed, especially close to opponent.
        if use_unclaimed:
            # Distance to nearest unclaimed
            d_unc = 10**9
            for ux, uy in unclaimed:
                d = abs(nx - ux) + abs(ny - uy)
                if d < d_unc:
                    d_unc = d
            val += (1000 - d_unc) if d_unc < 10**9 else 0
        # Prefer moving away from opponent when we cannot flip.
        d_opp = abs(nx - ox) + abs(ny - oy)
        val += d_opp * 2

        # Slightly prefer moves that reduce distance to unclaimed target (deterministic).
        if use_unclaimed:
            # Tie-break by distance to closest unclaimed from current pos
            d_cur = 10**9
            for ux, uy in unclaimed:
                d = abs(sx - ux) + abs(sy - uy)
                if d < d_cur:
                    d_cur = d
            val += (d_cur - (abs(nx - unclaimed[0][0]) + abs(ny - unclaimed[0][1]))) * 0  # no-op, deterministic placeholder removed

        # Deterministic tie-breaker: lexicographic on move.
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move