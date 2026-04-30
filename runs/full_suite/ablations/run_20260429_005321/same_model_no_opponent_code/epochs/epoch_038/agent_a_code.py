def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(ox, oy), (sx, sy)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    turn = int(observation.get("turn_index", 0) or 0)

    best_r = resources[0]
    best_key = None
    for r in resources:
        rx, ry = r
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        advantage = d2 - d1
        key = (-advantage, d1, (rx + ry) % 2, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = r

    rx, ry = best_r
    pref = ((turn % 2) * 3)  # deterministic, small tie-break shift
    best_move = (0, 0)
    best_move_key = None
    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dnew = cheb(nx, ny, rx, ry)
        dcur = cheb(sx, sy, rx, ry)
        # Prefer progress; if not possible, prefer staying closer; mild deterrent to moving away
        progress = dcur - dnew
        # Also mildly avoid squares that allow opponent to be closer to the target
        opp_d = cheb(ox, oy, rx, ry)  # constant, but keeps structure deterministic
        key = (-progress, dnew, abs(nx - ox) + abs(ny - oy), (i + pref) % 7, nx, ny)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]