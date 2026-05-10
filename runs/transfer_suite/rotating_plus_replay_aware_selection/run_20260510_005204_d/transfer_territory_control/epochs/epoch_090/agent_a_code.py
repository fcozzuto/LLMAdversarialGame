def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    resources = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.add((x, y))

    self_cells = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            self_cells.add((int(p[0]), int(p[1])))

    opp_cells = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            opp_cells.add((int(p[0]), int(p[1])))

    if resources:
        tx, ty = min(resources, key=lambda q: man(q[0], q[1], sx, sy))
        tx, ty = min(resources, key=lambda q: man(q[0], q[1], sx, sy) * 2 + man(q[0], q[1], ox, oy))
    else:
        tx, ty = ox, oy

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = None
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        v = -man(nx, ny, tx, ty)
        if (nx, ny) in resources:
            v += 50
        if (nx, ny) == (ox, oy):
            v += 200
        if (nx, ny) in opp_cells:
            v += 40
        if (nx, ny) in self_cells:
            v += 10
        if nx == ox and ny == oy:
            v += 100
        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best