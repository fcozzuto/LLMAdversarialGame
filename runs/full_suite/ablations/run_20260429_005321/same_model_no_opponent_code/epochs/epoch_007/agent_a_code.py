def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((x, y))
        except Exception:
            pass

    resources = []
    for p in observation.get("resources", []) or []:
        try:
            x, y = p
            resources.append((x, y))
        except Exception:
            pass
    if not resources:
        resources = None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_v = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        if resources is not None:
            minr = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < minr:
                    minr = d
            minO = cheb(nx, ny, ox, oy)
            v = -minr * 10 + minO
        else:
            minO = cheb(nx, ny, ox, oy)
            v = minO
        if v > best_v:
            best_v = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]