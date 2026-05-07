def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    w = observation["grid_width"]
    h = observation["grid_height"]

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    def best_target(px, py):
        best_key = None
        best_t = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(px, py, rx, ry)
            if sd == 0:
                sd = 0
            od = cheb(ox, oy, rx, ry)
            # Prefer resources on opponent's sweep row; also slight preference for targets closer in time.
            adv = od - sd
            intercept_bonus = 2.5 if ry == oy else 0.0
            row_pressure = -0.12 * abs(ry - oy)
            # Prefer targets that are not "behind" an immediate step away from them.
            closer_hint = 0.25 if sd < cheb(px, py, rx, ry) else 0.0
            key = (adv + intercept_bonus + row_pressure + closer_hint, -sd, -abs(rx - px) - abs(ry - py))
            if best_key is None or key > best_key:
                best_key = key
                best_t = (rx, ry)
        return best_t

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        t = best_target(nx, ny)
        if t is None:
            score = (-10**9, 0)
        else:
            tx, ty = t
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            adv = od - sd
            intercept_bonus = 2.5 if ty == oy else 0.0
            row_pressure = -0.12 * abs(ty - oy)
            # Small bias to make progress toward the chosen target.
            prog = -(abs(tx - nx) + abs(ty - ny))
            score = (adv + intercept_bonus + row_pressure, prog)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move