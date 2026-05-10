def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    sr = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in sr) or ("runner" in sr) or ("escape" in sr) or ("flee" in sr)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # deterministic tie-break order
    moves.sort(key=lambda d: (d[0], d[1]))

    def count_moves(px, py):
        c = 0
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if ok(nx, ny):
                c += 1
        return c

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # mobility term: evader prefers low self mobility next step; pursuer prefers low opponent mobility next step
        self_mob = count_moves(nx, ny)
        opp_mob = count_moves(ox, oy)  # opponent current mobility proxy (cheap, deterministic)
        # slight wall bias to avoid oscillation: prefer staying away from nearest border when evading, toward border when chasing
        border = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
        if is_evader:
            score = (d2 * 100) - (self_mob * 3) + (border * 1) - (dx * 0.1) - (dy * 0.01)
        else:
            score = (-d2 * 100) - (opp_mob * 2) - (self_mob * 0.3) + (-border * 0.5) - (dx * 0.1) - (dy * 0.01)

        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]