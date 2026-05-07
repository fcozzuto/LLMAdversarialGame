def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    moves = []
    cur = (sx, sy)
    if cur in resources:
        return [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            best_res = None
            bestd = None
            for rx, ry in resources:
                d = dist(nx, ny, rx, ry)
                if bestd is None or d < bestd or (d == bestd and (rx, ry) < best_res):
                    bestd = d
                    best_res = (rx, ry)
            dopp = dist(nx, ny, ox, oy)
            moves.append((bestd, -dopp, dx, dy))

    if not moves:
        return [0, 0]

    moves.sort()
    return [int(moves[0][2]), int(moves[0][3])]