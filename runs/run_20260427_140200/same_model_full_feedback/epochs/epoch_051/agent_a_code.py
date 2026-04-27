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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            dirs.append((dx, dy))

    best_score = -10**18
    best_move = (0, 0)

    if not resources:
        # Move towards center while avoiding obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            sc = -d
            if sc > best_score or (sc == best_score and (dx, dy) < best_move):
                best_score, best_move = sc, (dx, dy)
        return [best_move[0], best_move[1]]

    # Deterministic tie-break: smallest (dx,dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # If already adjacent to a resource, capture pressure is highest
        sc = 0
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Advantage: prefer resources where we can arrive no later than opponent
            adv = (do - ds)
            # Encourage being closer as well; heavily penalize being much farther
            sc += adv * 50 - ds * 3
            # Extra focus on immediate capture
            if ds == 0:
                sc += 500
            elif ds == 1:
                sc += 120
        # Slightly discourage wasting moves far from any resource "mass"
        dmin_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        sc -= dmin_self * 5

        if sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score, best_move = sc, (dx, dy)

    return [best_move[0], best_move[1]]