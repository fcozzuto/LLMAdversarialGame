def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    self_is_evader = "evader" in self_role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if self_is_evader:
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        tx, ty = ox, oy

    def mobility(x, y):
        m = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                m += 1
        return m

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # 2-step deterministic lookahead (avoid trapping when evading; avoid detours when pursuing)
        score = 0
        if self_is_evader:
            d1 = abs(nx - ox) + abs(ny - oy)
            score += 10 * d1
            score += 2 * (mobility(nx, ny))
            # prefer moving closer to a far corner from the pursuer
            d_corner_now = abs(nx - tx) + abs(ny - ty)
            score -= d_corner_now * 0.25
            # second step: assume pursuer doesn't help, maximize our eventual distance
            # deterministically choose our best continuation from (nx,ny)
            best2 = -10**9
            for ddx, ddy in moves:
                nnx, nny = nx + ddx, ny + ddy
                if not ok(nnx, nny):
                    continue
                d2 = abs(nnx - ox) + abs(nny - oy)
                sc2 = 10 * d2 + 2 * mobility(nnx, nny) - (abs(nnx - tx) + abs(nny - ty)) * 0.25
                if sc2 > best2:
                    best2 = sc2
            score += best2 * 0.35
        else:
            d1 = abs(nx - ox) + abs(ny - oy)
            score += -10 * d1
            score += 1.5 * mobility(nx, ny)
            # also prefer aligning toward opponent (simple waypoint = opponent)
            score -= (abs(nx - tx) + abs(ny - ty)) * 0.05
            best2 = -10**9
            for ddx, ddy in moves:
                nnx, nny = nx + ddx, ny + ddy
                if not ok(nnx, nny):
                    continue
                d2 = abs(nnx - ox) + abs(nny - oy)
                sc2 = -10 * d2 + 1.5 * mobility(nnx, nny) - (abs(nnx - tx) + abs(nny - ty)) * 0.05
                if sc2 > best2:
                    best2 = sc2
            score += best2 * 0.35

        # deterministic tie-break: prefer larger x-delta then y-delta then staying
        key = (score, dx, dy, 0 if (dx == 0 and dy == 0) else 1)
        if best is None or score > bestv:
            bestv = score
            best = [dx, dy]
        elif score == bestv:
            if key > (bestv, best[0], best[1], 0 if (best[0] == 0 and best[1] == 0) else 1):
                best = [dx, dy]

    return best if best is not None else [0, 0]