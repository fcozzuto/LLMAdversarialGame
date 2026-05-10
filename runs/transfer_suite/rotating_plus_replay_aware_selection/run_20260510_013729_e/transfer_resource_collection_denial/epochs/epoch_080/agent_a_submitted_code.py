def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set(obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    # Pick nearest resource by Manhattan distance
    tx, ty = resources[0]
    best = man(sx, sy, tx, ty)
    for rx, ry in resources[1:]:
        d = man(sx, sy, rx, ry)
        if d < best:
            best = d
            tx, ty = rx, ry

    # Greedy: prefer moves that reduce distance to (tx,ty), avoid blocks, tie-break deterministically
    best_move = [0, 0]
    best_val = 10**9
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not legal(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        # small penalty if moving into opponent proximity
        opp_pen = 0
        if man(nx, ny, ox, oy) <= 1:
            opp_pen = 2
        val = d + opp_pen
        if val < best_val:
            best_val = val
            best_move = [mdx, mdy]
        elif val == best_val and (mdx, mdy) < (best_move[0], best_move[1]):
            best_move = [mdx, mdy]

    return best_move