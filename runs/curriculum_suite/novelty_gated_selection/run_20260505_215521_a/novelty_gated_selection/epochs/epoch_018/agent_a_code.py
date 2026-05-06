def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    if resources:
        tgt = None
        bestd = 10**18
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                d = man(sx, sy, rx, ry)
                if d < bestd:
                    bestd = d
                    tgt = (rx, ry)
    else:
        tgt = (0 if ox > (w - 1) // 2 else w - 1, 0 if oy > (h - 1) // 2 else h - 1)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        v = -man(nx, ny, tgt[0], tgt[1])
        v -= 0.1 * man(nx, ny, ox, oy)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    nx, ny = sx + best_move[0], sy + best_move[1]
    if not inb(nx, ny) or (nx, ny) in obst:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]
    return [best_move[0], best_move[1]]