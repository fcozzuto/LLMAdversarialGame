def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    is_evader = "evad" in self_role

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best_move = (0, 0)
    if is_evader:
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = dist2(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < best_move):
                bestv = v
                best_move = (dx, dy)
    else:
        bestv = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = dist2(nx, ny, ox, oy)
            if v < bestv or (v == bestv and (dx, dy) < best_move):
                bestv = v
                best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]