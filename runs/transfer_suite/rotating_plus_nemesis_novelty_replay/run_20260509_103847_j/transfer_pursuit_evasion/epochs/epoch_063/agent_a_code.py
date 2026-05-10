def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) or ("escape" in role) or ("evade" in role) or ("runner" in role)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def free_nbr(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inside(nx, ny):
                c += 1
        return c

    def clamp(v, a, b):
        return a if v < a else (b if v > b else v)

    # Prefer zigzag interception: aim to reduce distance, but bias toward "cut" by moving toward opponent's projected half-step direction
    rvx = ox - sx
    rvy = oy - sy
    # projected target favors axis alignment to catch diagonal zigzags
    projx = ox - (1 if rvx > 0 else (-1 if rvx < 0 else 0)) * (2 if abs(rvx) >= abs(rvy) else 1)
    projy = oy - (1 if rvy > 0 else (-1 if rvy < 0 else 0)) * (2 if abs(rvy) > abs(rvx) else 1)
    projx = clamp(projx, 0, w - 1)
    projy = clamp(projy, 0, h - 1)

    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # avoid getting stuck behind obstacles: favor larger mobility
        mob = free_nbr(nx, ny)
        d_cur = abs(nx - ox) + abs(ny - oy)
        d_proj = abs(nx - projx) + abs(ny - projy)
        # slight center bias to keep maneuverability
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = -((nx - cx) ** 2 + (ny - cy) ** 2) * 0.005

        if i_am_evader:
            sc = (d_cur * 1.0) + (0.6 * d_proj) + (mob * 0.25) + center
        else:
            sc = (-d_cur * 1.0) + (-0.45 * d_proj) + (mob * 0.18) + center

        # deterministic tie-break: fixed move ordering preference
        if best is None or sc > best_sc + 1e-12:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]