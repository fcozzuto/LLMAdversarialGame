def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = (observation.get("self_role", "") or "").lower()
    pursuer = ("pursuer" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("guard" in self_role) or ("evader" not in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if sx == ox and sy == oy:
        return [0, 0]

    # Evader prefers running toward the farther corner (from pursuer); pursuer prefers directly shrinking distance.
    far_corner = (0, 0)
    if (ox + oy) <= ((w - 1) + (h - 1)):
        far_corner = (w - 1, h - 1)
    else:
        far_corner = (0, 0)

    best = None
    if pursuer:
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            # capture happens if equal positions
            dist = abs(nx - ox) + abs(ny - oy)
            on_top = 1 if (nx == ox and ny == oy) else 0
            # small bias toward diagonal progress and staying away from obstacles via wall/obstacle pressure
            wall_pen = (1 if nx in (-1, w) else 0) + (1 if ny in (-1, h) else 0)
            score = (1000000 if on_top else 0) + (-dist * 100) + (-(dx * (ox - sx) + dy * (oy - sy))) - wall_pen
            # tie-breaker: prefer moves that reduce dx+dy absolute changes deterministically
            score -= (abs(dx) + abs(dy)) * 0.001
            if score > best_score:
                best_score = score
                best = (dx, dy)
    else:
        best_score = 10**18
        tx, ty = far_corner
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dist = abs(nx - ox) + abs(ny - oy)
            # avoid immediate capture if possible
            on_top = 1 if (nx == ox and ny == oy) else 0
            # heading toward corner while maximizing distance
            corner_dist = abs(tx - nx) + abs(ty - ny)
            # obstacle/wall soft penalty: discourage moving into tight borders to keep mobility
            mobility = 0
            for ddx, ddy in moves:
                px, py = nx + ddx, ny + ddy
                if inb(px, py):
                    mobility += 1
            score = (0 if on_top else 1) * (-dist) + (dist)  # baseline to keep deterministic sign
            # convert to a minimization-style objective
            obj = (0 if not on_top else 10**9) - dist * 100 + corner_dist * (-1) - mobility * 0.5
            # deterministic tie-break: prefer larger move magnitude when scores are equal
            obj -= (abs(dx) + abs(dy)) * 0.0001
            if obj < best_score:
                best_score = obj
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]