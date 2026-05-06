def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not valid(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_move = [0, 0]
    best_score = None

    if res:
        def dist2(x1, y1, x2, y2):
            dx, dy = x1 - x2, y1 - y2
            return dx*dx + dy*dy
        target = min(res, key=lambda t: (dist2(sx, sy, t[0], t[1]), t[0], t[1]))
        tx, ty = target
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, tx, ty)
            opp_d = dist2(nx, ny, ox, oy)
            score = (-d, -opp_d, dx, dy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # If no resources, keep distance from opponent while staying roughly centered around them.
        opp_d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        center_bias = -abs((nx - (w - 1) / 2)) - abs((ny - (h - 1) / 2))
        score = (opp_d, center_bias, -abs(dx) - abs(dy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move