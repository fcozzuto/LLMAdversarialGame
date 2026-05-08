def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    valid = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y):
                valid.append((x, y))
    if not valid:
        # Move to maximize distance from opponent (deterministic).
        best = None
        for dx, dy, nx, ny in cand:
            key = (man(nx, ny, ox, oy), -man(nx, ny, sx, sy), dx, dy)
            if best is None or key > best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    best_key = None
    best_dx, best_dy = 0, 0
    for dx, dy, nx, ny in cand:
        # Prefer actions that give advantage to "win" a resource this move/soon:
        # minimize (myd - opd); tie-break by smaller myd, then larger total myd/opd slack.
        local_best = None
        for rx, ry in valid:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            adv = myd - opd
            key = (adv, myd, -(myd + opd), rx, ry)
            if local_best is None or key < local_best:
                local_best = key
        # Also lightly prefer moves that progress toward the best resource.
        combined = (local_best[0], local_best[1], local_best[2], dx, dy)
        if best_key is None or combined < best_key:
            best_key = combined
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]