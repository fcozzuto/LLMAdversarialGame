def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    i_am_pursuer = any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def cheb(x, y, tx, ty):
        dx = abs(x - tx)
        dy = abs(y - ty)
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    # deterministic move ordering: prefer staying if equally good, else fixed priority
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    cap_r = int(observation.get("capture_radius", 0) or 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        onto = (d <= cap_r)

        # obstacle "soft penalty": discourage hugging obstacles by counting blocked neighbors
        neigh_block = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if 0 <= px < w and 0 <= py < h and (px, py) in blocked:
                    neigh_block += 1

        # deterministic tie-break term from dx,dy
        tie = (dx + 1) * 3 + (dy + 1)

        if i_am_pursuer:
            # capture wants minimum distance; capture gets big reward
            score = (-1000 if onto else 0) + (10.0 if onto else 0.0) + (-d) - 0.05 * neigh_block - 0.001 * tie
        else:
            # evader wants maximum distance; avoid moving onto pursuer
            score = (1000 if onto else 0) + (d) - 0.05 * neigh_block - 0.001 * tie

        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]