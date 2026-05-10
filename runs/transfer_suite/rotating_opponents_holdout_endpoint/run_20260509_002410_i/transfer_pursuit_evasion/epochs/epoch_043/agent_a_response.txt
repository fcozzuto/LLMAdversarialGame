def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    is_evader = (self_role == "evader") or ("evader" in self_role) or (opponent_role == "pursuer")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles
    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy
    def mobility(x, y):
        m = 0
        for ax, ay in deltas:
            nx, ny = x + ax, y + ay
            if inb(nx, ny) and not blocked(nx, ny):
                m += 1
        return m

    best_dx, best_dy = 0, 0
    best_val = None
    # deterministic tie-break: prefer move with smallest (dx,dy) index after value
    for i, (dx, dy) in enumerate(deltas):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d2 = dist2(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        # evader: maximize distance and mobility, discourage being near obstacles via mob; pursuer opposite
        val = (d2 if is_evader else -d2) + (0.25 * mob if is_evader else 0.05 * mob)
        if best_val is None or val > best_val or (val == best_val and i < deltas.index((best_dx, best_dy))):
            best_val = val
            best_dx, best_dy = dx, dy

    # If all blocked/invalid, stay
    return [int(best_dx), int(best_dy)]