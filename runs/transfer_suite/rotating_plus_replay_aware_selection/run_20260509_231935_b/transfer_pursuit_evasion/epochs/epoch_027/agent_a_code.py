def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_pursuer = ("purs" in sr and "evad" in sr) or ("purs" in sr and "evad" not in sr) or ("purs" not in sr and "evad" not in sr and "purs" in orr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return in_bounds(x, y) and (x, y) not in obs
    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy
    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            if safe(x + dx, y + dy):
                m += 1
        return m

    tx, ty = (ox, oy)
    if not self_is_pursuer:
        # deterministic evasion: either run directly away or strafe depending on turn parity
        vx, vy = sx - ox, sy - oy
        if abs(vx) >= abs(vy):
            perp = (0, 1 if (observation.get("turn_index", 0) or 0) % 2 == 0 else -1)
        else:
            perp = (1 if (observation.get("turn_index", 0) or 0) % 2 == 0 else -1, 0)
        mode_strafe = ((observation.get("turn_index", 0) or 0) % 2 == 1)
        if mode_strafe:
            # strafe: move to increase distance slightly while shifting sideways
            tx, ty = sx + perp[0], sy + perp[1]
            # keep within bounds by clamping toward far corner
            tx = 0 if tx < 0 else (w - 1 if tx >= w else tx)
            ty = 0 if ty < 0 else (h - 1 if ty >= h else ty)
        else:
            # run to farthest corner from opponent
            corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
            tx, ty = max(corners, key=lambda c: d2(c[0], c[1], ox, oy))

    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        if self_is_pursuer:
            score = -d2(nx, ny, ox, oy) * 10 + mobility(nx, ny)
            # slight tie-break: prefer reducing delta to opponent
            score += -(abs(nx - ox) + abs(ny - oy))
        else:
            # maximize distance from pursuer; also prefer moving toward evasion target
            score = d2(nx, ny, ox, oy) * 10 + mobility(nx, ny)
            score += -(d2(nx, ny, tx, ty))
        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]