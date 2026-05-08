def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def blocked(x, y):
        return (x, y) in obstacles or not inb(x, y)

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escape" in role) or ("runner" in role)

    dirs = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
    best_dxdy = dirs[0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d = dist(nx, ny, ox, oy)
        val = d if is_evader else -d
        if best_val is None or val > best_val:
            best_val = val
            best_dxdy = (dx, dy)

    dx, dy = best_dxdy
    return [int(dx), int(dy)]