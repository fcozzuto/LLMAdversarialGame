def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inside(x, y) and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort(key=lambda d: (d[0], d[1]))

    r = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in r) or ("chaser" in r) or ("hunter" in r)

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obs_penalty(x, y):
        if not obs:
            return 0
        # smaller is better for evader, larger is worse; use min manhattan
        md = 10**9
        for ax, ay in obs:
            d = abs(ax - x) + abs(ay - y)
            if d < md:
                md = d
        return md

    best_move = [0, 0]
    if is_pursuer:
        best_val = None
        best_mob = -1
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = dist2(nx, ny, ox, oy)
            mob = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if legal(tx, ty):
                    mob += 1
            # prioritize reducing distance; then maximize mobility; then tie by dx,dy from sorted iteration
            if best_val is None or v < best_val or (v == best_val and mob > best_mob):
                best_val, best_mob = v, mob
                best_move = [dx, dy]
        return best_move
    else:
        # evader: maximize distance; avoid moving next to obstacles; deterministic tie-break
        best_val = None
        best_obs = None
        best_mob = -1
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = dist2(nx, ny, ox, oy)
            obd = obs_penalty(nx, ny)  # larger better (farther)
            mob = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if legal(tx, ty):
                    mob += 1
            if best_val is None or v > best_val or (v == best_val and (best_obs is None or obd > best_obs)) or (v == best_val and obd == best_obs and mob > best_mob):
                best_val, best_obs, best_mob = v, obd, mob
                best_move = [dx, dy]
        return best_move