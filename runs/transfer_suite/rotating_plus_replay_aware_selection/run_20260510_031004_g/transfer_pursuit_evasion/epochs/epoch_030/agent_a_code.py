def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "") or "").lower()
    evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    pursuer = ("pursuer" in role) or ("chaser" in role)
    if not (evader or pursuer):
        evader = True

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    if evader:
        tx, ty = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
    else:
        tx, ty = min(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def free_neighbors(nx, ny):
        cnt = 0
        for dx2 in (-1, 0, 1):
            for dy2 in (-1, 0, 1):
                if dx2 == 0 and dy2 == 0:
                    continue
                px, py = nx + dx2, ny + dy2
                if in_bounds(px, py) and (px, py) not in obs_set:
                    cnt += 1
        return cnt

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        d_tgt = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        neigh = free_neighbors(nx, ny)
        wall_pen = 0 if neigh > 0 else 5
        if evader:
            score = d_opp - 0.7 * d_tgt + 0.15 * neigh - wall_pen
        else:
            score = -d_opp - 0.3 * d_tgt + 0.12 * neigh - wall_pen
        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]