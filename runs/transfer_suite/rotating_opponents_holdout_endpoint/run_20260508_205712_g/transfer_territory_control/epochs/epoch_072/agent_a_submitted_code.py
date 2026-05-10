def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            try:
                x, y = int(x), int(y)
            except:
                continue
            if inb(x, y):
                obstacles.add((x, y))

    self_ter = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if inb(x, y):
                self_ter.add((x, y))

    opp_ter = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if inb(x, y):
                opp_ter.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    uc = []
    for p in unclaimed:
        if p and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if inb(x, y) and (x, y) not in obstacles:
                uc.append((x, y))
        if len(uc) >= 80:
            break

    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    oxp = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(oxp[0]), int(oxp[1])
    turn = int(observation.get("turn_index") or 0)

    best = -10**18
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            score = -10**12
        else:
            score = 0
            if (nx, ny) in self_ter:
                score += 2
            if (nx, ny) in opp_ter:
                score -= 50 if turn < 5 else 10
            if (nx, ny) in uc:
                score += 25
            if uc:
                dmin = 10**9
                for t in uc:
                    dd = abs(t[0] - nx) + abs(t[1] - ny)
                    if dd < dmin:
                        dmin = dd
                score += -dmin
            d_op = abs(nx - ox) + abs(ny - oy)
            score += -0.2 * d_op
            if turn >= 10 and (nx, ny) in opp_ter:
                score += 30
        if score > best:
            best = score
            best_move = [dx, dy]

    return best_move