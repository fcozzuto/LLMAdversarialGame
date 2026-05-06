def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 1) or 1)
    h = int(observation.get("grid_height", 1) or 1)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is None:
            continue
        x, y = p
        obs.add((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    best_r = None
    best_d = None
    for r in resources:
        rx, ry = r
        rx, ry = int(rx), int(ry)
        d = cheb(sx, sy, rx, ry)
        if best_d is None or d < best_d:
            best_d = d
            best_r = (rx, ry)

    rx, ry = best_r
    oppd0 = cheb(sx, sy, ox, oy)

    candidates = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = cheb(nx, ny, rx, ry)
        od = cheb(nx, ny, ox, oy)
        val = -d * 10 + od - (abs(dx) + abs(dy))
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    if best_val is None:
        return [0, 0]
    return best_move