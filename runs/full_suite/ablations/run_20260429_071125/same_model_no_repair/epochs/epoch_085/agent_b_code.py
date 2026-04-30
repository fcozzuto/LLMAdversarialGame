def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            r = (int(p[0]), int(p[1]))
            if r not in obstacles:
                resources.append(r)
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = None
    tpar = int(observation.get("turn_index", 0)) & 1

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        best_over = None
        for rx, ry in resources:
            me = cheb(nx, ny, rx, ry)
            op = cheb(ox, oy, rx, ry)
            benefit = op - me  # positive => we are closer than opponent
            # Prefer strong contest/steal pressure; keep slight bias to nearer resources for us.
            val = benefit * 10 - me + (2 if (rx + ry) % 2 == tpar else 0) - (0.1 * (rx + ry))
            if best_over is None or val > best_over:
                best_over = val
        if best_over is None:
            continue

        tie = (int((nx + ny) % 2 == tpar), -cheb(nx, ny, ox, oy), -nx, -ny)
        cur = (best_over,) + tie
        if best_val is None or cur > best_val:
            best_val = cur
            best = (dx, dy)

    return [best[0], best[1]]