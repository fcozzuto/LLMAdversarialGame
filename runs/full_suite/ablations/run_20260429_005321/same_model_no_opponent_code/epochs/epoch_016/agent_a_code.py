def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            resources.append((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = (0, 0)
    best_val = -10**18
    has_res = False

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        val = -0.0
        if resources:
            has_res = True
            d = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            val += 200 - 20 * d
            d_opp = cheb(nx, ny, ox, oy)
            val -= 3 * d_opp
        else:
            d_opp = cheb(nx, ny, ox, oy)
            val += 10 - d_opp

        if val > best_val:
            best_val = val
            best = (dx, dy)

    if has_res:
        return [best[0], best[1]]

    # If no valid move found (shouldn't happen), stand still.
    return [int(best[0]), int(best[1])]