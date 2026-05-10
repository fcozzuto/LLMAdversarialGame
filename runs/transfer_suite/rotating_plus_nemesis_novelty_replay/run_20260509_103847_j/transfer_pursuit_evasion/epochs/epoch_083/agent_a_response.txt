def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role)

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def neighbors_toward(tx, ty):
        dxs = [-1, 0, 1]
        dys = [-1, 0, 1]
        best = None
        bestd = None
        for dx in dxs:
            for dy in dys:
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                if (nx, ny) in blocked:
                    continue
                d = abs(nx - tx) + abs(ny - ty)
                if best is None or d < bestd or (d == bestd and (dx, dy) == best):
                    best = (dx, dy)
                    bestd = d
        return best

    if is_evader:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        mv = neighbors_toward(tx, ty)
        if mv is not None:
            return [mv[0], mv[1]]
        dx = 0 if sx == clamp(sx, 0, w - 1) else (1 if sx < tx else -1)
        dy = 0 if sy == clamp(sy, 0, h - 1) else (1 if sy < ty else -1)
        return [int(dx), int(dy)]

    # pursuer: anticipate by aiming beyond opponent away from us
    aim_x = clamp(ox + (ox - sx), 0, w - 1)
    aim_y = clamp(oy + (oy - sy), 0, h - 1)
    mv = neighbors_toward(aim_x, aim_y)
    if mv is not None:
        return [mv[0], mv[1]]

    # fallback: greedy minimize distance to current opponent (still avoiding obstacles if possible)
    best = None
    bestd = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in blocked:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            if best is None or d < bestd:
                best = (dx, dy)
                bestd = d
    if best is not None:
        return [int(best[0]), int(best[1])]

    # if completely blocked, stay
    return [0, 0]