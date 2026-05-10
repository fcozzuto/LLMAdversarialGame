def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if cell_ok(x, y):
                unclaimed.append((x, y))

    cx, cy = w // 2, h // 2
    if unclaimed:
        best = None
        bestd = 10**9
        for x, y in unclaimed:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd:
                bestd = d
                best = (x, y)
        tx, ty = best
    else:
        tx, ty = cx, cy

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not cell_ok(nx, ny):
            continue
        if mx == dx and my == dy:
            return [mx, my]

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if cell_ok(nx, ny):
            return [mx, my]

    return [0, 0]