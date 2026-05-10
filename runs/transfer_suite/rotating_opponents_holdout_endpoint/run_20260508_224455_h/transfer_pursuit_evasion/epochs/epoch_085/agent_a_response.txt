def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    sr = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in sr) or ("hunter" in sr) or ("pred" in sr) or (sr == "pursuer")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def risk(x, y):
        r = 0
        for ex, ey in obs:
            dx, dy = x - ex, y - ey
            d2 = dx * dx + dy * dy
            if d2 == 0:
                return 10**9
            if d2 <= 4:  # near obstacle within 2
                r += (5 - d2)
        return r

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        rk = risk(nx, ny)

        # Puts pursuer closer and evader farther, with obstacle-avoidance.
        if is_pursuer:
            val = (-d2) - 0.25 * rk
            # Extra tie-break: prefer heading toward opponent (reduce manhattan if same d2).
            val -= 0.01 * (abs(nx - ox) + abs(ny - oy))
        else:
            val = (d2) - 0.25 * rk
            val += 0.01 * (abs(nx - ox) + abs(ny - oy))

        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]