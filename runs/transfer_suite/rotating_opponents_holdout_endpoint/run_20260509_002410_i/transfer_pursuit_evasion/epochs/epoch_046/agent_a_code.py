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
    is_evader = ("evader" in self_role) or (self_role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def move_ok(d):
        x, y = sx + d[0], sy + d[1]
        return inb(x, y) and not blocked(x, y)

    best_d = (0, 0)
    best_val = None
    for d in deltas:
        if not move_ok(d):
            continue
        nx, ny = sx + d[0], sy + d[1]
        d2 = dist(nx, ny, ox, oy)
        val = d2 if is_evader else -d2
        if best_val is None or val > best_val:
            best_val = val
            best_d = d

    return [int(best_d[0]), int(best_d[1])]