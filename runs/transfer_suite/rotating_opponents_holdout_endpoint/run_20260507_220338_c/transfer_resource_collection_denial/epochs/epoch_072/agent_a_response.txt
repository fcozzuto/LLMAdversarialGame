def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            q = (p[0], p[1])
            if q not in obst:
                res.append(q)

    moves = [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def nearest(fromx, fromy):
        if not res:
            return (ox, oy)
        best = None
        bd = None
        for rx, ry in res:
            d = man(fromx, fromy, rx, ry)
            if bd is None or d < bd or (d == bd and (rx, ry) < best):
                bd = d
                best = (rx, ry)
        return best

    my_t = nearest(sx, sy)
    op_t = nearest(ox, oy)

    if (sx, sy) in obst:
        tx, ty = ox, oy
    elif res:
        tx, ty = my_t
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        if (nx, ny) == (tx, ty) and res:
            my_dist = 0
        else:
            my_dist = man(nx, ny, tx, ty)
        op_dist = man(nx, ny, op_t[0], op_t[1]) if res else man(nx, ny, ox, oy)
        deny = 0
        if res:
            # Encourage blocking by staying closer to the opponent's target than them
            deny = 0.6 * (man(ox, oy, op_t[0], op_t[1]) - op_dist)
        else:
            deny = 0.2 * (man(ox, oy, nx, ny))
        val = (-1.0 * my_dist) + (0.35 * op_dist) + deny
        # Small deterministic preference for moving toward the target
        if dx == 0 and dy == 0:
            val -= 0.01
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]