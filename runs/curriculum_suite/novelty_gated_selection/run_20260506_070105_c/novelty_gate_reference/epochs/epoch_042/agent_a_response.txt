def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = resources[0]
    best_score = -10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer places we can reach first; small tie-break favors closer resource overall.
        score = (od - sd) * 1000 - sd
        if (od - sd) == 0:
            score -= (abs(rx - sx) + abs(ry - sy))
        if score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best[0], best[1]
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # Order directions by progress toward target, with obstacle safety first.
    def dir_key(dx, dy):
        nx, ny = sx + dx, sy + dy
        inb = (0 <= nx < w and 0 <= ny < h)
        obs = (nx, ny) in obstacles if inb else True
        ns = cheb(nx, ny, tx, ty) if inb and not obs else 10**9
        prog = cheb(sx, sy, tx, ty) - ns
        return (0 if (inb and not obs) else 1, -prog, abs(tx - (sx + dx)) + abs(ty - (sy + dy)))

    best_move = (0, 0)
    best_k = None
    for dx, dy in dirs:
        k = dir_key(dx, dy)
        if best_k is None or k < best_k:
            best_k = k
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]