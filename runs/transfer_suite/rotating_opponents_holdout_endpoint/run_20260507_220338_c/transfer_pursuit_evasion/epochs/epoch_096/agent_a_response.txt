def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    i_am_pursuer = any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y, tx, ty):
        dx = abs(x - tx)
        dy = abs(y - ty)
        return dx if dx >= dy else dy

    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    # Try to bias corner-running when evading, and "blocky" movement when pursuing.
    best = None
    best_move = (0, 0)
    turn = int(observation.get("turn_index", 0) or 0)

    # Deterministic tie-break: prefer moves in this fixed order.
    prefer_order = {(dx, dy): i for i, (dx, dy) in enumerate(moves)}

    # Choose a target corner for evasion: alternate between farthest/runner-up to change behavior.
    # For pursuit, we instead chase with obstacle-aware scoring.
    dists = [(cheb(cx, cy, ox, oy), i, (cx, cy)) for i, (cx, cy) in enumerate(corners)]
    dists.sort(reverse=True)
    far1 = dists[0][2]
    far2 = dists[1][2] if len(dists) > 1 else far1
    ev_target = far1 if (turn % 2 == 0) else far2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Mobility: fewer blocked neighbors can help pursuer; for evader, avoid being boxed in.
        open_cnt = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                open_cnt += 1

        # Obstacle-adjacency: avoid moving into tight wall corridors for evader; for pursuer, use them.
        wallish = 0
        for ax, ay in ((nx - 1, ny), (nx + 1, ny), (nx, ny - 1), (nx, ny + 1)):
            if not (0 <= ax < w and 0 <= ay < h) or (ax, ay) in blocked:
                wallish += 1

        if i_am_pursuer:
            # Reduce distance to opponent; slightly prefer higher open space to avoid getting stuck behind obstacles.
            dist_now = cheb(nx, ny, ox, oy)
            score = -10 * dist_now + 0.7 * open_cnt - 0.25 * wallish
        else:
            # Increase distance to opponent; also move toward a target corner and keep mobility.
            dist_now = cheb(nx, ny, ox, oy)
            to_t = cheb(nx, ny, ev_target[0], ev_target[1])
            score = 10 * dist_now - 0.8 * to_t + 0.25 * open_cnt - 0.2 * wallish

        key = (score, -prefer_order[(dx, dy)])
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]