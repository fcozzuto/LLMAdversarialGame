def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        best_adv = -10**9
        best_ds = 10**9
        for rx, ry in resources:
            dS = cheb(sx, sy, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            adv = dO - dS
            sTie = (dS < best_ds) if best is not None else True
            if adv > best_adv or (adv == best_adv and (best is None or sTie or (dS == best_ds and (rx + ry) < (best[0] + best[1])))):
                best = (rx, ry)
                best_adv = adv
                best_ds = dS
        tx, ty = best

    if (sx, sy) == (tx, ty):
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer reducing Chebyshev distance to target; tie-break by improving relative advantage.
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h: 
            continue
        if (nx, ny) in obstacles:
            continue
        dT = cheb(nx, ny, tx, ty)
        dS = cheb(nx, ny, tx, ty)
        dO = cheb(ox, oy, tx, ty)
        adv = dO - dS
        candidates.append((dT, -adv, 0, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    _, _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]