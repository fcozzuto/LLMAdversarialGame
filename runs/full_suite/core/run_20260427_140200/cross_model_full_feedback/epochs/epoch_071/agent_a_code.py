def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def pick_target():
        if resources:
            best = None
            bestkey = None
            for rx, ry in resources:
                k = (dist(mx, my, rx, ry), dist(ox, oy, rx, ry), rx, ry)
                if bestkey is None or k < bestkey:
                    bestkey = k
                    best = (rx, ry)
            return best
        return ((w - 1) // 2, (h - 1) // 2)

    tx, ty = pick_target()

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not inb(nx, ny):
            continue
        dme = dist(nx, ny, tx, ty)
        dopp = dist(nx, ny, ox, oy)
        k = (dme, -dopp, nx, ny)
        if best_key is None or k < best_key:
            best_key = k
            best_move = [dx, dy]

    if inb(mx, my):
        return best_move
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if inb(nx, ny):
            return [dx, dy]
    return [0, 0]