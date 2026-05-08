def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set(observation.get("obstacles"))
    self_t = to_set(observation.get("self_territory"))
    opp_t = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    resources = to_set(observation.get("resources"))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist_center = abs(nx - cx) + abs(ny - cy)
        opp_in = 1 if (nx, ny) in opp_t else 0
        uncl_in = 1 if (nx, ny) in unclaimed else 0
        self_in = 1 if (nx, ny) in self_t else 0
        res_in = 1 if (nx, ny) in resources else 0

        # Count "free" neighbors to prefer open lanes and reduce obstacle trapping.
        free_n = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                tx, ty = nx + ex, ny + ey
                if inb(tx, ty) and (tx, ty) not in obstacles:
                    free_n += 1

        # Deterministic opponent response: avoid mirroring their path too directly; contest near center.
        to_opp = abs(nx - ox) + abs(ny - oy)
        score = 0.0
        score += 12.0 * opp_in           # entering opponent-owned flips control
        score += 4.0 * uncl_in         # take expansion points
        score += 1.5 * self_in
        score += 2.0 * res_in
        score += 0.3 * free_n
        score += -0.8 * dist_center
        score += 0.05 * to_opp         # slight keep-away to reduce immediate contest losses
        candidates.append((score, dist_center, to_opp, nx, ny, dx, dy))

    # If somehow no valid moves (all blocked), stay still.
    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    _, _, _, _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]