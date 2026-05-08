def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    evading = any(k in role for k in ("evader", "evade", "runner", "flee", "evasion"))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clearance(x, y):
        c = 0
        for mx, my in deltas:
            nx, ny = x + mx, y + my
            if valid(nx, ny):
                c += 1
        return c

    def dist_to_obstacles(x, y):
        # small repulsion from nearby obstacles (no heavy computation)
        best = 10
        for oxp, oyp in obstacles:
            dx = x - oxp
            if dx < 0: dx = -dx
            dy = y - oyp
            if dy < 0: dy = -dy
            d = dx if dx > dy else dy
            if d < best:
                best = d
                if best <= 1:
                    break
        return best

    # Prefer moves that approach (pursuer) or escape (evader), while not stepping into cramped cells.
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        c = clearance(nx, ny)
        dob = dist_to_obstacles(nx, ny)
        # Base objective
        primary = d if evading else -d  # minimize distance if chasing; maximize if evading
        # Penalties/bonuses
        # - prefer open areas
        open_bonus = c if evading else c
        # - avoid walls/obstacles tightness
        tight_pen = 0 if dob >= 3 else (4 - dob)  # 0..3
        # - discourage cornering when chasing (tends to trap against wall runners)
        corner = (nx in (0, w - 1)) and (ny in (0, h - 1))
        corner_pen = 1 if corner else 0
        score = (primary * 1000) + (open_bonus * 10) - (tight_pen * 25) - (corner_pen * (6 if not evading else 0))
        # Deterministic tie-break: fixed delta ordering by list index
        idx = deltas.index((dx, dy))
        key = (score, idx)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    # Fallback (shouldn't happen unless surrounded by obstacles): stay put
    return best[1] if best is not None else [0, 0]