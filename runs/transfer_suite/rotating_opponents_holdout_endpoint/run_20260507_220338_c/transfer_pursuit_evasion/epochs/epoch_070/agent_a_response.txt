def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role", "")).lower()
    self_is_pursuer = ("pursuer" in role_s) or ("chaser" in role_s) or ("pursuit" in role_s) or ("catch" in role_s) or ("hunter" in role_s)
    # if not explicit, infer from environment name "pursuit_evasion": likely pursuer if role says so
    if not self_is_pursuer and ("evader" in role_s or "runner" in role_s or "flee" in role_s or "avoid" in role_s):
        self_is_pursuer = False
    elif not self_is_pursuer:
        # default: act as pursuer
        self_is_pursuer = True

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    d_old = cheb(sx, sy, ox, oy)

    best_dx, best_dy = 0, 0
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        d_new = cheb(nx, ny, ox, oy)

        # Greedy with small tie-break toward diagonal progress and away from dead-ends
        # dead-end penalty: count free neighbors from candidate
        deg = 0
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in blocked:
                deg += 1

        # tie-breaker: prefer moving in the dominant direction toward/away from opponent
        sxgn = 0 if ox == nx else (1 if ox > nx else -1)
        sygn = 0 if oy == ny else (1 if oy > ny else -1)
        diag_bias = 0
        if dx != 0 and dy != 0 and (sxgn != 0 and sygn != 0):
            diag_bias = 1
        align_bias = abs((1 if dx > 0 else (-1 if dx < 0 else 0)) - sxgn) + abs((1 if dy > 0 else (-1 if dy < 0 else 0)) - sygn)

        if self_is_pursuer:
            # minimize distance; if tie, prefer higher "deg" and better diagonal alignment
            key = (d_new, -deg, align_bias, -diag_bias, nx + ny)
            choose = best_key is None or key < best_key
        else:
            # maximize distance; if tie, prefer higher "deg" and better escape alignment
            key = (-d_new, -deg, align_bias, -diag_bias, -(nx + ny))
            choose = best_key is None or key < best_key

        if choose:
            best_key = key
            best_dx, best_dy = dx, dy

    # if all moves blocked (shouldn't happen), stay
    return [int(best_dx), int(best_dy)]