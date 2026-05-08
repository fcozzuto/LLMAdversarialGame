def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            c = (int(p[0]), int(p[1]))
            if 0 <= c[0] < w and 0 <= c[1] < h and c not in obstacles:
                unclaimed.append(c)

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            c = (int(p[0]), int(p[1]))
            if 0 <= c[0] < w and 0 <= c[1] < h and c not in obstacles:
                resources.append(c)

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Build targets: prefer unclaimed; otherwise resources; otherwise opponent position.
    targets = unclaimed
    if not targets:
        targets = resources
    if not targets:
        targets = [(ox, oy)]

    # Secondary bias: avoid moving toward opponent if they are close.
    opp_close = man(sx, sy, ox, oy) <= 2

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Find nearest target distance
        dmin = 10**9
        for tx, ty in targets:
            d = man(nx, ny, tx, ty)
            if d < dmin:
                dmin = d
        # Score: primary minimize distance to target; secondary avoid opponent if close; tertiary prefer expanding into unclaimed.
        score = dmin
        if opp_close:
            score += max(0, 4 - man(nx, ny, ox, oy)) * 2
        if (nx, ny) in self_terr:
            score -= 1
        # Prefer stepping into unclaimed if available
        if unclaimed and (nx, ny) in unclaimed:
            score -= 3
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        # Fallback: stay if possible, else first valid move.
        if inb(sx, sy) and (sx, sy) not in obstacles:
            return [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    return [best[1], best[2]]