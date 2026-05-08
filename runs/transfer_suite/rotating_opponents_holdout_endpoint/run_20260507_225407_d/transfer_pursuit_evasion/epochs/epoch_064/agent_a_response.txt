def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("evasion" in r) or ("avoid" in r)

    self_role = observation.get("self_role", "") or ""
    if not is_evader(self_role):
        self_role = observation.get("self_role_name", "") or self_role
    if not is_evader(self_role):
        self_role = observation.get("role", "") or self_role
    evading = is_evader(self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_d2 = (sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)

    best = None
    best_sc = None
    prefer = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    order = []
    for m in prefer:
        if m in moves and m not in order:
            order.append(m)
    for m in moves:
        if m not in order:
            order.append(m)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if evading:
            score = (d2 - cur_d2)
            if nx == ox and ny == oy:
                score -= 1000000  # avoid capture
            # bias away from obstacles locally (prefer safer squares)
            npen = 0
            for ax, ay in [(-1,0),(1,0),(0,-1),(0,1)]:
                tx, ty = nx + ax, ny + ay
                if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obstacles:
                    npen += 1
            score += -0.2 * npen
            # bias toward opposite corner from pursuer
            corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
            farc = max(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), -c[0], -c[1]))
            score += 0.01 * ((abs(farc[0] - nx) + abs(farc[1] - ny)) - (abs(farc[0] - sx) + abs(farc[1] - sy)))
        else:
            score = (cur_d2 - d2)
            if nx == ox and ny == oy:
                score += 1000000  # capture
            # avoid moving into obstacle-adjacent dead zones a bit
            npen = 0
            for ax, ay in [(-1,0),(1,0),(0,-1),(0,1)]:
                tx, ty = nx + ax, ny + ay
                if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obstacles:
                    npen += 1
            score += -0.05 * npen

        if best_sc is None or score > best_sc:
            best_sc = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best