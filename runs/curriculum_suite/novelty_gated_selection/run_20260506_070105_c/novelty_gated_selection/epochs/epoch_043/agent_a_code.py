def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = []
    for r in (observation.get("resources", []) or []):
        rt = (int(r[0]), int(r[1]))
        if rt not in obstacles:
            resources.append(rt)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            val = md(nx, ny, ox, oy)
            if val > best_val:
                best_val, best_move = val, [dx, dy]
        return best_move

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        best_here = -10**18
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            oppd = md(ox, oy, rx, ry)
            val = (oppd - myd) * 100 - myd
            if val > best_here:
                best_here = val
        if best_here > best_val:
            best_val, best_move = best_here, [dx, dy]

    return best_move