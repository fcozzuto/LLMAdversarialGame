def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_mv = [0, 0]

    def mhd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_for_move = -10**9
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = r[0], r[1]
            if not valid(rx, ry):
                continue
            ds = mhd(nx, ny, rx, ry)
            do = mhd(ox, oy, rx, ry)
            score = (do - ds) * 1000 - ds
            if score > best_for_move:
                best_for_move = score

        cand = (best_for_move, -abs(dx) - abs(dy), -dx, -dy)
        if best is None or cand > best:
            best = cand
            best_mv = [dx, dy]

    return best_mv if valid(sx + best_mv[0], sy + best_mv[1]) else [0, 0]