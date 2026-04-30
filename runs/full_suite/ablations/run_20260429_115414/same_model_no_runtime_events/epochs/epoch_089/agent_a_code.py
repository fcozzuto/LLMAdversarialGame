def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx = 1 if sx < w - 1 - sx else 0 if sx == w - 1 - sx else -1
        ty = 1 if sy < h - 1 - sy else 0 if sy == h - 1 - sy else -1
        nx, ny = sx + tx, sy + ty
        if valid(nx, ny): return [tx, ty]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    best_key = None
    # Target where we are relatively closer than opponent; if none, pick where opponent is farthest.
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer
        key = (0, -adv, ds, rx, ry) if adv > 0 else (1, -do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    tx = 0 if rx == sx else (1 if rx > sx else -1)
    ty = 0 if ry == sy else (1 if ry > sy else -1)

    # Move that minimizes our cheb distance to target, tie-breakers prefer reducing opponent reach.
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        ns = cheb(nx, ny, rx, ry)
        no = cheb(ox, oy, rx, ry)
        my_adv = no - ns
        # If we can step to be closer than opponent, prioritize that; else minimize ns and maximize my_adv.
        score = (0 if my_adv > 0 else 1, ns, -my_adv, abs((nx + ny) - (ox + oy)), dx, dy)
        cand.append((score, dx, dy))
    if cand:
        cand.sort()
        return [int(cand[0][1]), int(cand[0][2])]

    # Fallback: move toward target if possible
    nx, ny = sx + tx, sy + ty
    if valid(nx, ny): return [tx, ty]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny): return [dx, dy]
    return [0, 0]