def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        candidates = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    def best_target():
        best = None
        bestd = 10**9
        for x, y in resources:
            d = abs(sx - x) + abs(sy - y)
            if d < bestd:
                bestd = d
                best = (x, y)
        return best

    tx, ty = best_target()
    dx = 0 if sx == tx else (1 if tx > sx else -1)
    dy = 0 if sy == ty else (1 if ty > sy else -1)

    moves = []
    for cand in [(dx, dy), (dx, 0), (0, dy), (0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]:
        mx, my = cand
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            moves.append((mx, my))

    if not moves:
        return [0, 0]
    best = None
    bestscore = -10**18
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        d_me = abs(nx - tx) + abs(ny - ty)
        d_op = abs(ox - tx) + abs(oy - ty)
        score = -d_me + (0.1 if (ox != nx or oy != ny) else 0) + (0.01 if d_me <= d_op else 0)
        if score > bestscore:
            bestscore = score
            best = (mx, my)
    return [int(best[0]), int(best[1])]