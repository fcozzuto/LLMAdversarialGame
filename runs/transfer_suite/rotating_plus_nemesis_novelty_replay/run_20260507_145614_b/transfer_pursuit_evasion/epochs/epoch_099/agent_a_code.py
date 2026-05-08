def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    pursuer = ("pursuer" in self_role) or ("catcher" in self_role) or ("evader" in opp_role)

    moves = [(0, 0), (1, 1), (-1, -1), (1, -1), (-1, 1), (1, 0), (-1, 0), (0, 1), (0, -1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    # Deterministic corner bias: helps when roles mismatch or direct chase stalls.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    t = int(observation.get("turn_index", 0) or 0)
    corner_bias = corners[t % 4]

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        dc = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        db = dist2(nx, ny, corner_bias[0], corner_bias[1])
        # pursuer: reduce distance, prefer center (less escape surface)
        # evader: increase distance, prefer opposite corner bias
        if pursuer:
            val = (-d) * 10.0 - dc * 0.01 + db * 0.001
        else:
            val = (d) * 10.0 + db * 0.01 - dc * 0.002

        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]