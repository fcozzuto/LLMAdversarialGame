def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def manh(x, y, a, b):
        dx = x - a
        if dx < 0:
            dx = -dx
        dy = y - b
        if dy < 0:
            dy = -dy
        return dx + dy

    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in self_role) or (self_role in ("captor", "pursuer"))
    evader = not pursuer

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # deterministic tie-break
    moves = sorted(moves, key=lambda m: (m[0], m[1]))

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    best_move = [0, 0]
    if evader:
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = manh(nx, ny, ox, oy)
            # Prefer staying away, but also avoid getting cornered by pulling toward center when distance is similar
            center_bias = (abs(nx - cx) + abs(ny - cy))
            # Higher is better
            val = d * 10 - center_bias
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = manh(nx, ny, ox, oy)
            # Lower distance is better; also discourage staying still unless forced
            stay_pen = 0 if (dx == 0 and dy == 0) else 1
            val = (-d, -stay_pen)
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]