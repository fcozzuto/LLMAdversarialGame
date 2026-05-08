def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role_s = str(observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role_s) or ("chase" in role_s) or ("hunter" in role_s)
    is_evader = ("evad" in role_s) or ("run" in role_s) or ("away" in role_s) or ("escape" in role_s) or ("runner" in role_s)
    if not (is_pursuer or is_evader):
        is_pursuer = True

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def corner_bias(x, y):
        # Encourage/Discourage corners depending on role via multiplier outside.
        return min(x, w - 1 - x) + min(y, h - 1 - y)

    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)

        # Local obstacle pressure: prefer positions with more legal neighboring squares.
        ncount = 0
        for adx, ady in deltas:
            tx, ty = nx + adx, ny + ady
            if in_bounds(tx, ty):
                ncount += 1

        # Anticipate that opponent may try to align; add a small directional term.
        align = -abs((nx - ox)) - abs((ny - oy))  # smaller is better for pursuer, larger for evader

        if is_pursuer:
            # Main objective: minimize distance; secondary: avoid being boxed; tertiary: move toward corner when close.
            val = (-d) + 0.05 * ncount + 0.003 * (corner_bias(nx, ny) * (-1)) + 0.001 * align
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < tuple(best_move))
        else:
            # Evader: maximize distance; prefer keeping mobility; prefer not entering tight corners.
            val = (d) + 0.05 * ncount - 0.01 * corner_bias(nx, ny) + 0.001 * (-align)
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < tuple(best_move))

        if better:
            best_val = val
            best_move = [dx, dy]

    return best_move