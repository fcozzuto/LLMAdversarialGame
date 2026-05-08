def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("evader" in role)

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obstacle_penalty(x, y):
        # Prefer cells with more open neighbors (helps against wall-run archetypes)
        pen = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not ok(nx, ny):
                pen += 1
        return pen

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    fc_x, fc_y = far_corner

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_to_opp = dist2(nx, ny, ox, oy)
        pen = obstacle_penalty(nx, ny)

        if is_evader:
            # Primary: maximize distance from pursuer
            # Secondary: head toward farthest corner from pursuer
            d_corner = dist2(nx, ny, fc_x, fc_y)
            val = (d_to_opp, d_corner, -pen, -dx, -dy)
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)
        else:
            # Pursuer: minimize distance, prefer less constrained cells
            val = (-d_to_opp, -pen, dx, dy)
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]