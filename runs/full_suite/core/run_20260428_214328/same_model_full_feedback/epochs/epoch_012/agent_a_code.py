def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            dres = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            lead = -dres
        else:
            dres = cheb(nx, ny, cx, cy)
            lead = -dres

        dopp = cheb(nx, ny, ox, oy)
        score = lead * 100 + dopp  # prefer resource closeness, then distance from opponent

        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        best = (0, 0)
        if not inb(sx, sy) or (sx, sy) in obstacles:
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    best = (dx, dy)
                    break

    return [int(best[0]), int(best[1])]