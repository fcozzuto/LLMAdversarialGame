def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        t = a - c
        if t < 0:
            t = -t
        u = b - d
        if u < 0:
            u = -u
        return t + u

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**18, 0, 0)

    if not resources:
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (not inb(nx, ny)) or ((nx, ny) in obs):
            continue

        # Evaluate best target after this move
        best_val_here = -10**18
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            tx, ty = r[0], r[1]
            if not inb(tx, ty) or (tx, ty) in obs:
                continue
            self_d = md(tx, ty, nx, ny)
            opp_d = md(tx, ty, ox, oy)
            # Prefer resources where we can get there first (advantage), and with closer proximity.
            # Also slightly prefer moving toward center-ish to avoid dead ends.
            center_bias = -0.02 * (md(tx, ty, (w - 1) / 2, (h - 1) / 2))
            val = (opp_d - self_d) * 10.0 - self_d * 1.0 + center_bias
            if val > best_val_here:
                best_val_here = val

        # Tie-break deterministically by prefer diagonal-less (stay stable), then lexicographic
        stability = -0.1 * (abs(dx) + abs(dy))
        val2 = best_val_here + stability
        if val2 > best[0]:
            best = (val2, dx, dy)
        elif val2 == best[0]:
            if (abs(dx) + abs(dy)) < (abs(best[1]) + abs(best[2])):
                best = (val2, dx, dy)
            elif (abs(dx) + abs(dy)) == (abs(best[1]) + abs(best[2])) and (dx, dy) < (best[1], best[2]):
                best = (val2, dx, dy)

    return [int(best[1]), int(best[2])]