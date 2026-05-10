def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = True
    if "evad" in self_role:
        is_pursuer = False
    elif "evad" in opp_role:
        is_pursuer = True

    obs = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    near_corner = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_dxdy = (0, 0)
    if is_pursuer:
        target = far_corner  # chase along a line that pulls evader away from you
        best = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # primary: reduce distance to opponent
            d_opp = md((nx, ny), (ox, oy))
            # secondary: align movement toward far corner (reduce distance from evader's likely corner)
            d_t = md((nx, ny), target)
            score = (-d_opp * 10) + (-d_t)
            if score > best:
                best = score
                best_dxdy = (dx, dy)
        return [best_dxdy[0], best_dxdy[1]]
    else:
        target = far_corner  # run to the opposite corner from pursuer
        best = -10**9
        # if target blocked, encourage escaping from pursuer while still moving generally toward target
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_opp = md((nx, ny), (ox, oy))
            d_t = md((nx, ny), target)
            # avoid making self easy to corner: also keep away from near corner relative to opponent
            d_near = md((nx, ny), near_corner)
            score = (d_opp * 10) - d_t + d_near
            if score > best:
                best = score
                best_dxdy = (dx, dy)
        # fallback: always maximize distance if all moves blocked except staying
        if best_dxdy == (0, 0):
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if valid(nx, ny):
                    if md((nx, ny), (ox, oy)) > md((sx, sy), (ox, oy)):
                        best_dxdy = (dx, dy)
                        break
        return [best_dxdy[0], best_dxdy[1]]