def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))
        except:
            pass

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    oppd0 = man(sx, sy, ox, oy)
    if not resources:
        best = min(legal, key=lambda t: (-man(sx + t[0], sy + t[1], ox, oy), t[0], t[1]))
        return [int(best[0]), int(best[1])]

    best_score = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        mind = min(man(nx, ny, rx, ry) for rx, ry in resources)
        oppd = man(nx, ny, ox, oy)
        # Prefer smaller resource distance, larger separation from opponent
        sc = (-mind, -oppd, dx, dy)
        if best_score is None or sc < best_score:
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]