def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for it in observation.get("obstacles", []) or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    i_am_pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("pursue" in self_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx >= dy else dy

    # Deterministic obstacle-aware steering toward/away from opponent
    best_move = [0, 0]
    best_score = -10**18 if i_am_pursuer else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, ox, oy)
        # Wall-running: prefer moves that keep distance change consistent and don't "hug" obstacles too tightly.
        # Compute how constrained the next position is (number of free neighboring cells).
        free = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if inside(tx, ty) and (tx, ty) not in obstacles:
                free += 1
        # Pursuer: minimize distance, then maximize freedom; Evader: maximize distance, then maximize freedom.
        score = (-dist, free) if i_am_pursuer else (dist, free)
        if i_am_pursuer:
            cur = score[0] * 10**6 + score[1]
            if cur > best_score:
                best_score = cur
                best_move = [dx, dy]
        else:
            cur = score[0] * 10**6 + score[1]
            if cur < best_score:
                best_score = cur
                best_move = [dx, dy]

    # If all moves blocked (unlikely), fall back to deterministic direct step or stay.
    if best_move == [0, 0] and (sx, sy) not in obstacles:
        step_dx = 0 if ox == sx else (1 if ox > sx else -1)
        step_dy = 0 if oy == sy else (1 if oy > sy else -1)
        if i_am_pursuer:
            cand = [step_dx, step_dy]
        else:
            cand = [-step_dx, -step_dy]
        ndx, ndy = cand[0], cand[1]
        nx, ny = sx + ndx, sy + ndy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            return [ndx, ndy]
    return best_move