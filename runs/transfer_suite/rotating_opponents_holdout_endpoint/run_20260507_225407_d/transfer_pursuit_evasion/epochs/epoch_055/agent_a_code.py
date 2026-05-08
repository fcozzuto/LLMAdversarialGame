def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evasion" in self_role) or ("avoid" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def open_space(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best_move = (0, 0)
    best_val = None
    # Deterministic tie-break by fixed move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        os = open_space(nx, ny)
        corner_term = dist2(nx, ny, far_corner[0], far_corner[1]) if is_evader else dist2(nx, ny, near_corner[0], near_corner[1])
        # Pursuer tries to get close; Evader tries to get far and reach far_corner.
        if is_evader:
            val = d + 3.0 * corner_term + 0.2 * os
        else:
            val = -d + 0.2 * os - 0.5 * corner_term * 0.0001  # tiny, keeps determinism without overfitting
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]