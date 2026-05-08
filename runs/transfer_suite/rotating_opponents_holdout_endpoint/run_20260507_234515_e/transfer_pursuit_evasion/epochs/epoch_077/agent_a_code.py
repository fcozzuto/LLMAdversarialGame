def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    rset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                rset.add((x, y))

    resources = observation.get("resources", []) or []
    resources_list = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in rset:
                resources_list.append((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in rset

    def cheb(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx > dy else dy

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_res = min((cheb(nx, ny, rx, ry) for rx, ry in resources_list), default=10**9)
        on_resource = (nx, ny) in set(resources_list)  # small set; deterministic
        score = (1000 if on_resource else 0) + (d_opp * 10) - d_res
        if score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best