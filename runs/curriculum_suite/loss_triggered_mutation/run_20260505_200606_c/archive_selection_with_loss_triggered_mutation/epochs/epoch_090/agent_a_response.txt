def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    if not resources:
        resources = [[-1, -1]]

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def order(x, y):
        x, y = int(x), int(y)
        return x * h + (y if (x % 2 == 0) else (h - 1 - y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_o = order(sx, sy)

    # tie-breakers
    nearest_res = None
    best_near = 10**9
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        d = man(sx, sy, rx, ry)
        if d < best_near:
            best_near = d
            nearest_res = (rx, ry)
    nrx, nry = nearest_res

    best = None  # (primary, secondary, dx, dy) where higher primary better
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        no = order(nx, ny)
        primary = no  # advance along traversal
        # discourages backing up and getting stuck near opponent
        backup_pen = 1000 if no < cur_o else 0
        near_op = man(nx, ny, ox, oy)
        near_res = man(nx, ny, nrx, nry)
        secondary = -(backup_pen + near_res) + (-near_op * 0.01)
        cand = (primary, secondary, dx, dy)
        if best is None or cand > best:
            best = cand

    return [best[2], best[3]] if best is not None else [0, 0]