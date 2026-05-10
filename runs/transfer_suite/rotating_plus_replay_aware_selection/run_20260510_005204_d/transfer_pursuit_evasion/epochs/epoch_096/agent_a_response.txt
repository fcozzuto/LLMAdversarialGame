def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evade" in role) or ("escape" in role)
    env = str(observation.get("environment_name", "")).lower()
    if any(k in env for k in ["evader", "runner", "evade", "escape"]):
        is_evader = True

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = corners[0]
    best_d = -10**9
    for cx, cy in corners:
        d = (cx - ox) * (cx - ox) + (cy - oy) * (cy - oy)
        if d > best_d:
            best_d = d
            best_corner = (cx, cy)

    tcx, tcy = best_corner if is_evader else (ox, oy)

    def score(nx, ny):
        if (nx, ny) in blocked:
            return -10**12
        if not inb(nx, ny):
            return -10**12
        dxo, dyo = nx - ox, ny - oy
        dist_opp2 = dxo * dxo + dyo * dyo
        d_goal2 = (nx - tcx) * (nx - tcx) + (ny - tcy) * (ny - tcy)
        if is_evader:
            return dist_opp2 * 2.0 + d_goal2 * -0.15
        return (-dist_opp2) * 1.8 + d_goal2 * -0.15

    # Deterministic tie-break: fixed order moves
    best = moves[0]
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = score(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]