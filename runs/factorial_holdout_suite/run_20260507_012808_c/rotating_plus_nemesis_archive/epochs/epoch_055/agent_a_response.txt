def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def best_score(px, py):
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry) and not (rx == px and ry == py):
                continue
            sd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            can_take = 1 if sd <= od else -1
            score = can_take * 50 + (od - sd) * 10 - sd
            if best is None or score > best:
                best = score
        return best if best is not None else -10**9

    best_move = (0, 0)
    best_val = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = best_score(nx, ny) - cheb(nx, ny, ox, oy) * 0.5
            if v > best_val:
                best_val = v
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]