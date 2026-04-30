def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    my_step = None
    if not resources:
        nx = sx
        ny = sy
        for dx, dy in dirs:
            tx, ty = sx + dx, sy + dy
            if not valid(tx, ty):
                continue
            if cheb(tx, ty, ox, oy) > cheb(nx, ny, ox, oy):
                nx, ny = tx, ty
        return [nx - sx, ny - sy]

    best_dir = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        tx, ty = sx + dx, sy + dy
        if not valid(tx, ty):
            continue

        # Greedy: choose move maximizing "being closer than opponent" to a good resource.
        # Also slightly prefer reducing my distance.
        best_local = -10**18
        for rx, ry in resources:
            myd = cheb(tx, ty, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where I can reach at least as fast, and minimize time-to-go.
            # Weight: primary by advantage, secondary by absolute time-to-go.
            adv = opd - myd
            val = adv * 100 - myd
            if val > best_local:
                best_local = val

        # Tie-break: keep from walking away from all resources.
        if best_local > best_val:
            best_val = best_local
            my_step = (dx, dy)

    if my_step is None:
        return [0, 0]
    return [int(my_step[0]), int(my_step[1])]