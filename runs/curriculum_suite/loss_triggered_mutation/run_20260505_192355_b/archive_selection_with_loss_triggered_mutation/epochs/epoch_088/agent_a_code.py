def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                targets.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not inb(sx, sy):
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    best = None
    bestd = 10**9
    for tx, ty in targets:
        d = abs(sx - tx) + abs(sy - ty)
        if d < bestd:
            bestd = d
            best = (tx, ty)

    if best is not None:
        tx, ty = best
        step_dx = 0 if tx == sx else (1 if tx > sx else -1)
        step_dy = 0 if ty == sy else (1 if ty > sy else -1)
        cand = [(step_dx, step_dy), (step_dx, 0), (0, step_dy), (0, 0)]
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (abs(nx - tx) + abs(ny - ty)) < bestd:
                return [dx, dy]
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    dx = 0 if cx == sx else (1 if cx > sx else -1)
    dy = 0 if cy == sy else (1 if cy > sy else -1)
    for px, py in [(dx, dy), (dx, 0), (0, dy), (-dx, -dy), (0, 0)]:
        nx, ny = sx + px, sy + py
        if inb(nx, ny):
            if (nx, ny) != (ox, oy):
                return [px, py]
    for px, py in moves:
        nx, ny = sx + px, sy + py
        if inb(nx, ny):
            return [px, py]
    return [0, 0]