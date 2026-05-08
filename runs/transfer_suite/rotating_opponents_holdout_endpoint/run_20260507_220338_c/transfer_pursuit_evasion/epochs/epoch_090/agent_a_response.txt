def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    i_am_evader = not any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def cheb(x, y, tx, ty):
        dx = abs(x - tx)
        dy = abs(y - ty)
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    best = None
    best_val = None
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            # Additional preference: keep moving when possible by slightly rewarding diagonal/orth moves
            step_bias = 0
            if dx != 0 or dy != 0:
                step_bias = 0.001 * (abs(dx) + abs(dy))
            # If evader: maximize distance; pursuer: minimize distance
            val = dist + step_bias if i_am_evader else -dist - step_bias
            if best is None or val > best_val:
                best = (dx, dy)
                best_val = val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]