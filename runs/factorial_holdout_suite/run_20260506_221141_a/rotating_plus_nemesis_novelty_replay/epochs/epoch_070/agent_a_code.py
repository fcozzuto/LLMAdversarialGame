def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    obs_set = set()
    for p in observation.get("obstacles") or []:
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

    def md(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    # Pick a target resource with strongest "beat opponent" margin.
    best_t = None
    best_key = None
    for tx, ty in resources:
        sd = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        # Prefer winning margin; break ties by smaller self distance; then deterministic by coord.
        key = (od - sd, -sd, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t

    # Choose move that improves chance to reach target before opponent and avoids obstacles.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    best_m_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue

        self_d = md(nx, ny, tx, ty)
        opp_d = md(ox, oy, tx, ty)
        # Main objective: increase margin (opp_d - self_d).
        # Secondary: prioritize immediate progress to the target.
        # Tertiary: deterministic tie-break by move vector.
        margin = opp_d - self_d
        key = (margin, -self_d, -abs(nx - tx) - abs(ny - ty), -dx, -dy)
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]