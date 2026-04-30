def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obst = set()
    for p in obstacles:
        try:
            x, y = p
            obst.add((int(x), int(y)))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    rs = []
    for r in resources:
        try:
            x, y = r
            rs.append((int(x), int(y)))
        except:
            pass

    if not rs:
        dx, dy = min(moves)
        return [dx, dy]

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d_self = min(cheb(nx, ny, rx, ry) for rx, ry in rs)
        d_opp = min(cheb(ox, oy, rx, ry) for rx, ry in rs)
        score = (d_opp - d_self, -d_self, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]