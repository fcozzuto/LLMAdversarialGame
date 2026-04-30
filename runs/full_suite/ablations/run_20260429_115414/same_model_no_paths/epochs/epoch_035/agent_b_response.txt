def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Drift toward opponent to contest territory deterministically.
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                v = -cheb(nx, ny, ox, oy)
                if v > bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    # Pick best resource: strongly prefer those we can reach no later than opponent.
    target = resources[0]
    bestt = -10**18
    for rx, ry in resources:
        dm = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Bias: reach-first > closeness > opponent closeness
        t = (1 if dm <= do else 0) * 10_000 + (do - dm) * 50 - dm
        # Slight preference for center-ish to reduce getting stuck (deterministic).
        t -= abs(rx - (w - 1) / 2) * 0.1 + abs(ry - (h - 1) / 2) * 0.1
        if t > bestt:
            bestt = t
            target = (rx, ry)

    rx, ry = target

    # Move to neighbor that maximizes our advantage over opponent toward the target.
    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles):
            continue
        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Strongly enforce approach while keeping an advantage.
        v = (1 if myd <= opd else 0) * 10_000 + (opd - myd) * 60 - myd
        if (nx, ny) == (rx, ry):
            v += 50_000
        # Tiny deterministic tie-break favoring moves with smaller (dx,dy) lexicographic.
        v -= (abs(dx) + abs(dy)) * 0.01
        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best