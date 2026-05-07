def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh

    obs = observation.get("obstacles") or []
    obs_set = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obs_set.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs_set:
                resources.append((rx, ry))

    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if sx == cx else (1 if cx > sx else -1)
        dy = 0 if sy == cy else (1 if cy > sy else -1)
        return [dx, dy]

    def cd(a, b, c, d):  # Chebyshev distance for 8-dir step including diagonals
        ax = a - c
        if ax < 0: ax = -ax
        by = b - d
        if by < 0: by = -by
        return ax if ax > by else by

    best = None
    for tx, ty in resources:
        sd = cd(sx, sy, tx, ty)
        od = cd(ox, oy, tx, ty)
        advantage = od - sd
        # Prefer bigger advantage; if tie, prefer closer to us; then deterministic by position.
        key = (advantage, -sd, -tx, -ty)
        if best is None or key > best[0]:
            best = (key, tx, ty)
    _, tx, ty = best

    tx_step = 0 if sx == tx else (1 if tx > sx else -1)
    ty_step = 0 if sy == ty else (1 if ty > sy else -1)

    candidates = []
    # Priority: diagonal toward target, then straight axes, then stay.
    candidates.append((tx_step, ty_step))
    candidates.append((tx_step, 0))
    candidates.append((0, ty_step))
    candidates.append((tx_step, -ty_step))
    candidates.append((-tx_step, ty_step))
    candidates.append((0, 0))

    # Deterministic filter and tie-break by resulting Chebyshev distance to target.
    def cell_ok(dx, dy):
        nx, ny = sx + dx, sy + dy
        return inb(nx, ny) and (nx, ny) not in obs_set

    valid = []
    for dx, dy in candidates:
        if dx in (-1, 0, 1) and dy in (-1, 0, 1) and cell_ok(dx, dy):
            nx, ny = sx + dx, sy + dy
            valid.append((cd(nx, ny, tx, ty), dx, dy, nx, ny))

    if not valid:
        # If all blocked, stay still (engine will keep us in place).
        return [0, 0]

    valid.sort(key=lambda z: (z[0], z[1], z[2], z[3], z[4]))
    return [int(valid[0][1]), int(valid[0][2])]