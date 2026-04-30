def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked
    def cd(a, b, c, d):
        dx = a - c; dx = -dx if dx < 0 else dx
        dy = b - d; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    viable = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            viable.append((dx, dy, nx, ny))
    if not viable:
        return [0, 0]
    best_target = None
    best_adv = None
    for r in resources:
        rx, ry = r[0], r[1]
        if not legal(rx, ry):
            continue
        sd = cd(sx, sy, rx, ry)
        od = cd(ox, oy, rx, ry)
        adv = od - sd
        if best_adv is None or adv > best_adv:
            best_adv = adv
            best_target = (rx, ry)
    if best_target is None:
        return [0, 0]
    tx, ty = best_target
    best = None
    best_move = (0, 0)
    for dx, dy, nx, ny in viable:
        sd = cd(nx, ny, tx, ty)
        od = cd(ox, oy, tx, ty)
        v = -sd
        v += 2 if (nx, ny) == (tx, ty) else 0
        if od <= cd(ox, oy, tx, ty):
            v += 0
        if (nx, ny) == (ox, oy):
            v -= 10
        if best is None or v > best or (v == best and (dx, dy) < best_move):
            best = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]