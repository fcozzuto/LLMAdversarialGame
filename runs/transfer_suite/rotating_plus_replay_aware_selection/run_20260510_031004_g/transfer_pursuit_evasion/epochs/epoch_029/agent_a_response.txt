def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "") or "").lower()
    evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    pursuer = ("pursuer" in role) or ("chaser" in role)
    if not (evader or pursuer):
        evader = True

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    if evader:
        tx, ty = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
    else:
        tx, ty = min(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))

    def blocked(nx, ny):
        if (nx, ny) in obs_set:
            return True
        # dead-end proxy: count adjacent free cells
        free = 0
        for dx2 in (-1, 0, 1):
            for dy2 in (-1, 0, 1):
                if dx2 == 0 and dy2 == 0:
                    continue
                xx, yy = nx + dx2, ny + dy2
                if 0 <= xx < w and 0 <= yy < h and (xx, yy) not in obs_set:
                    free += 1
        return free == 0

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue

        dxo, dyo = nx - ox, ny - oy
        dist2 = dxo * dxo + dyo * dyo

        dxt, dyt = nx - tx, ny - ty
        toward2 = dxt * dxt + dyt * dyt

        if (nx, ny) == (ox, oy):
            val = (10**9) if pursuer else (-10**9)
        else:
            # discourage traps for evader, avoid them for pursuer
            trap_pen = 50 if blocked(nx, ny) else 0
            if evader:
                val = (dist2 * 10) - toward2 - trap_pen
            else:
                val = (-dist2 * 10) - toward2 - trap_pen

        # Deterministic tie-break: lexicographic by (dx,dy) preference order in moves list
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]