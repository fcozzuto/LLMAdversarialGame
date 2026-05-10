def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_list:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    dirs = [-1, 0, 1]
    moves = []
    for dx in dirs:
        for dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy))
    moves.append((0, 0))
    if not moves:
        return [0, 0]

    # Pick resource we can reach first (tie-break by best margin then coordinates).
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not (0 <= rx < w and 0 <= ry < h):
            continue
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        margin = d_op - d_me  # higher is better (we closer)
        key = (-(margin), d_me, d_op, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r

    # Move toward target with obstacle-safe immediate validity, minimizing (our dist, opponent dist, dx, dy).
    cur_d_me = cheb(sx, sy, rx, ry)
    best_move = None
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d_me2 = cheb(nx, ny, rx, ry)
        d_op2 = cheb(ox, oy, rx, ry)
        # Encourage reducing our distance; if equal, prefer moves that don't help opponent race (keep us stable).
        mkey = (d_me2, -(d_op2 - d_me2), d_op2, abs(dx) + abs(dy), dx, dy)
        if d_me2 <= cur_d_me + 2:
            if best_mkey is None or mkey < best_mkey:
                best_mkey = mkey
                best_move = (dx, dy)
    if best_move is None:
        best_move = (0, 0)

    return [int(best_move[0]), int(best_move[1])]