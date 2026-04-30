def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**18
    best_tie = 10**18

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            cand.append((nx, ny, dx, dy))

    if not cand:
        return [0, 0]

    if resources:
        for nx, ny, dx, dy in cand:
            # Value: best advantage over any reachable resource from this next position.
            # Tie-break: prefer smaller self distance to that chosen resource.
            local_best = -10**18
            local_self = 10**18
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                oppd = cheb(ox, oy, rx, ry)
                adv = oppd - myd
                if adv > local_best or (adv == local_best and myd < local_self):
                    local_best = adv
                    local_self = myd
            # Small secondary preference: closer to currently most "contested" targets (small myd, large adv).
            score = local_best * 1000 - local_self
            if score > best_val or (score == best_val and local_self < best_tie):
                best_val = score
                best_tie = local_self
                best = [dx, dy]
    else:
        # No visible resources: drift toward the center while reducing distance to opponent less than them (deterministic).
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for nx, ny, dx, dy in cand:
            myc = cheb(nx, ny, cx, cy)
            opcc = cheb(ox, oy, cx, cy)
            # Prefer moving closer to center; if equal, prefer moving away from opponent a bit.
            score = -myc * 10 + (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy))
            if score > best_val or (score == best_val and myc < best_tie):
                best_val = score
                best_tie = myc
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best