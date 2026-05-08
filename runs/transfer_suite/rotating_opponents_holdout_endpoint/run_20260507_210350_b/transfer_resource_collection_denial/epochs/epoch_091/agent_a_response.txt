def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def king(a, b, c, d):
        return abs(a - c) if abs(a - c) >= abs(b - d) else abs(b - d)

    # Prefer resources where we arrive no later than opponent, and where opponent is "behind".
    opp_best = min(resources, key=lambda t: (king(ox, oy, t[0], t[1]), t[0], t[1]))

    best_t = resources[0]
    best_val = -10**9
    for t in resources:
        myd = king(sx, sy, t[0], t[1])
        opd = king(ox, oy, t[0], t[1])
        faster = 1 if myd < opd else (0 if myd == opd else -1)
        depr = 1 if t == opp_best else 0
        val = (opd - myd) + 0.8 * faster - 0.15 * depr - 0.02 * myd
        if (val > best_val) or (val == best_val and (t[0], t[1]) < (best_t[0], best_t[1])):
            best_val, best_t = val, t

    tx, ty = best_t
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If next step hits obstacle (possible if resources list excludes but move doesn't), choose best alternative.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
        candidates = []
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                cx, cy = sx + ddx, sy + ddy
                if 0 <= cx < w and 0 <= cy < h and (cx, cy) not in obstacles:
                    myd2 = king(cx, cy, tx, ty)
                    opd2 = king(ox, oy, tx, ty)
                    val2 = (opd2 - myd2) - 0.01 * myd2
                    candidates.append((val2, cx, cy))
        if candidates:
            candidates.sort(key=lambda z: (-z[0], z[1], z[2]))
            _, nx, ny = candidates[0]
            dx, dy = nx - sx, ny - sy
        else:
            dx, dy = 0, 0

    return [int(dx), int(dy)]