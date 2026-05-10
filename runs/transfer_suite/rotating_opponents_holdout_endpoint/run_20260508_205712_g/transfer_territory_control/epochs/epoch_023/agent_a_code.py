def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    unclaimed = observation.get("unclaimed_cells", []) or []
    uc = set((int(x), int(y)) for x, y in unclaimed)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if uc:
        tx, ty = min(uc, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        tx, ty = ox, oy

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        v = -man(nx, ny, tx, ty)
        if (nx, ny) in uc:
            v += 1000 - man(nx, ny, tx, ty)
        v += 0.01 * man(nx, ny, ox, oy)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    return best_move