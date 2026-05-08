def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Target: maximize (opponent advantage), tie-break for faster/self-closer and centrality.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        advantage = od - sd
        center_bias = abs((rx - (w - 1 - sx)) - (ry - (h - 1 - sy)))
        key = (advantage, -sd, -center_bias, -rx - ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    # Local step selection with obstacle avoidance and improving capture chance.
    dxs = (-1, 0, 1)
    candidates = []
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obst:
                continue
            ds_self = man(nx, ny, tx, ty)
            ds_now = man(sx, sy, tx, ty)
            ds_opp = man(ox, oy, tx, ty)
            # Prefer moving closer to target; if equal, prefer moves that increase relative lead.
            move_score = (-(ds_self), -(ds_self - ds_now), (ds_opp - ds_self), -abs(nx - (w - 1 - ox)) - abs(ny - (h - 1 - oy)))
            candidates.append((move_score, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]