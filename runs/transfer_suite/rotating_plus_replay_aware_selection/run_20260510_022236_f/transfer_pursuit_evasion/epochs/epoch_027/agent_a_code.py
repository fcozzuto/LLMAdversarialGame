def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) and ("purs" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def score(nx, ny):
        # Base: pursue/minimize or evade/maximize distance.
        d = dist2(nx, ny, ox, oy)
        base = -d if not is_evader else d

        # Obstacle proximity penalty (deterministic).
        pen = 0
        for (bx, by) in obs:
            dd = (nx - bx) * (nx - bx) + (ny - by) * (ny - by)
            if dd == 0:
                pen -= 10_000
            else:
                pen -= 40 // (1 + dd)  # stronger near obstacles

        # Prefer mobility: evader wants escape paths; pursuer wants room to maneuver.
        mob = 0
        for dx, dy in moves:
            tx, ty = nx + dx, ny + dy
            if ok(tx, ty):
                mob += 1
        mob_term = (mob if is_evader else -mob)

        # Add mild center/edge shaping to reduce zigzag corner-stalling.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        center_term = (-center_d if is_evader else center_d)

        return base + pen + 2.0 * mob_term + 0.03 * center_term

    best_s = None
    best_m = [0, 0]
    # Deterministic tie-break: fixed move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        s = score(nx, ny)
        if best_s is None or s > best_s:
            best_s = s
            best_m = [dx, dy]

    return best_m