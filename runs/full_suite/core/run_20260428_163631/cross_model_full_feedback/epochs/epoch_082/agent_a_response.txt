def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def manh(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    opp_next = set()
    for dx, dy in deltas:
        tx, ty = ox + dx, oy + dy
        if inb(tx, ty) and (tx, ty) not in obstacles:
            opp_next.add((tx, ty))

    if not resources:
        # Drift away from opponent if possible, else toward center-ish.
        best = None
        for dx, dy, nx, ny in legal:
            away = manh(nx, ny, ox, oy)
            center = abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)
            score = away * 100 - center
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [int(best[1]), int(best[2])]

    best_move = None
    for dx, dy, nx, ny in legal:
        # Strongly discourage stepping where opponent can go next (contested).
        contested = 1 if (nx, ny) in opp_next else 0
        # Pick the resource where our advantage (opponent distance - our distance) is largest.
        best_adv = -10**9
        for rx, ry in resources:
            myd = manh(nx, ny, rx, ry)
            opd = manh(ox, oy, rx, ry)
            adv = opd - myd
            if adv > best_adv:
                best_adv = adv
        # Mild tie-break: also prefer being closer than opponent to that same best resource.
        # Approximate by comparing distances to the nearest resource from our next position.
        nearest_my = min(manh(nx, ny, rx, ry) for rx, ry in resources)
        nearest_op = min(manh(ox, oy, rx, ry) for rx, ry in resources)
        score = best_adv * 1000 + (nearest_op - nearest_my) * 10 - contested * 500
        if best_move is None or score > best_move[0]:
            best_move = (score, dx, dy)
    return [int(best_move[1]), int(best_move[2])]