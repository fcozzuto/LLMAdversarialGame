def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    my = (sx, sy)
    opp = (ox, oy)

    if not resources:
        tx, ty = w // 2, h // 2
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            sc = -cheb((nx, ny), (tx, ty))
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    best_sc = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        me2 = (nx, ny)
        sc = 0
        # Prefer grabbing: being on a resource is best.
        if (nx, ny) in resources:
            sc += 10**6
        # Compete: resources where we can get closer than opponent matter more.
        for r in resources:
            dme = cheb(me2, r)
            dop = cheb(opp, r)
            # Higher when we reduce gap and when opponent is far.
            sc += (dop - dme) * 120
            # Slight penalty for being far from any resource (keeps moving purposefully).
            sc -= dme * 2
        # Avoid letting opponent instantly take: discourage moves that keep us too far from the closest contested resource.
        closest = 10**9
        for r in resources:
            closest = min(closest, cheb(my, r))
        sc -= max(0, closest - cheb(me2, resources[0])) * 1  # tiny deterministic bias
        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]