def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    if not resources:
        cx, cy = w // 2, h // 2
        dx = 0 if sx == cx else (1 if cx > sx else -1)
        dy = 0 if sy == cy else (1 if cy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        # fall back: choose any valid step that decreases cheb distance to center
        best = None
        best_d = 10**9
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                nx, ny = sx + ddx, sy + ddy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    d = (abs(nx - cx) if abs(nx - cx) > abs(ny - cy) else abs(ny - cy))
                    if d < best_d:
                        best_d = d
                        best = [ddx, ddy]
        return best if best is not None else [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = w // 2, h // 2

    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive => we are earlier
        own_center = cheb(rx, ry, cx, cy)
        # Prefer earlier captures; if tied, prefer nearer and then closer to center to avoid corner traps.
        key = (lead * 1000) - ds - 2 * own_center
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = None
    best_score = None
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            nx, ny = sx + ddx, sy + ddy
            if not valid(nx, ny):
                continue
            dnew = cheb(nx, ny, tx, ty)
            dopp = cheb(ox, oy, tx, ty)
            lead_after = dopp - dnew
            # tiny bias to avoid dithering: prefer moves that reduce distance most
            score = (lead_after * 2000) - dnew - 0.1 * cheb(nx, ny, cx, cy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [ddx, ddy]
    return best_move if best_move is not None else [0, 0]