def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    s = observation.get("self_position", [0, 0])
    o = observation.get("opponent_position", [0, 0])
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    if resources:
        nearest = min(resources, key=lambda r: cheb(sx, sy, r[0], r[1]))
        rx0, ry0 = nearest
    else:
        rx0, ry0 = (0, 0)

    chase = (int(observation.get("turn_index", 0)) % 2 == 1)
    rem = int(observation.get("remaining_resource_count", len(resources)))
    w_res = 1.0 if resources else 0.0
    w_op = 0.35 if chase else 0.2
    w_corner = 0.12 if rem <= 5 else 0.04

    # Corner bias to diversify routes when resources are scarce/blocked
    target_corner = (0, 7) if (sx + sy) % 2 == 0 else (7, 0)

    best = None
    best_sc = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if resources:
            dres = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        else:
            dres = cheb(nx, ny, rx0, ry0)

        dop = cheb(nx, ny, ox, oy)
        dcorn = cheb(nx, ny, target_corner[0], target_corner[1])

        # Main: minimize resource distance; Secondary: either compete (closer to opponent) or avoid.
        sc = (-w_res * dres) + (w_op * (-dop if chase else dop)) + (-w_corner * dcorn)
        if best_sc is None or sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    return [best[0], best[1]]