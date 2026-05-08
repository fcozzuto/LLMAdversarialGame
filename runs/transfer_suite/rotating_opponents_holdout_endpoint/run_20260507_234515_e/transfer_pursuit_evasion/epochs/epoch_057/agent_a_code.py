def choose_move(observation):
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role)
    if ("pursuer" in role) or ("hunter" in role):
        is_evader = False

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obstacle_proximity(x, y):
        best = 10**9
        for (px, py) in oset:
            d = abs(x - px) + abs(y - py)
            if d < best:
                best = d
                if best == 0:
                    return 0
        return best

    def corner_target_score(x, y):
        return max(md(x, y, cx, cy) for (cx, cy) in corners)

    def score_cell(x, y):
        d = md(x, y, ox, oy)
        # add small deterministic tie-breakers for better corner play (evader) / direct chase (pursuer)
        if is_evader:
            return d * 10 + corner_target_score(x, y) - obstacle_proximity(x, y)
        else:
            return -d * 10 - md(x, y, sx, sy) - 0.3 * obstacle_proximity(x, y)

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in oset:
            continue
        # 2-step lookahead (keeping opponent fixed; deterministic greedy continuation)
        best2 = -10**18 if is_evader else 10**18
        for ddx, ddy in moves:
            nnx, nny = nx + ddx, ny + ddy
            if not inside(nnx, nny) or (nnx, nny) in oset:
                continue
            val = score_cell(nnx, nny)
            if is_evader:
                if val > best2:
                    best2 = val
            else:
                if val < best2:
                    best2 = val
        val1 = score_cell(nx, ny)
        total = (best2 + 0.15 * val1) if is_evader else (best2 + 0.15 * val1)
        if best is None or (total > best if is_evader else total < best):
            best = total
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]