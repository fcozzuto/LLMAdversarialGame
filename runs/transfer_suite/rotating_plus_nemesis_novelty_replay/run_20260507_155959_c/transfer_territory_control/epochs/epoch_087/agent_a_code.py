def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = set()
    for c in observation.get("self_territory") or []:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                self_t.add((x, y))

    opp_t = set()
    for c in observation.get("opponent_territory") or []:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                opp_t.add((x, y))

    unclaimed = []
    for c in observation.get("unclaimed_cells") or []:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1),(0,0)]
    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        score = 0
        score += 2 if (nx, ny) in self_t else 0
        score -= 2 if (nx, ny) in opp_t else 0

        if unclaimed:
            dmin = None
            for ux, uy in unclaimed:
                d = abs(nx - ux) + abs(ny - uy)
                if dmin is None or d < dmin:
                    dmin = d
            score -= dmin

        d_to_opp = abs(nx - ox) + abs(ny - oy)
        d_cur = abs(sx - ox) + abs(sy - oy)
        if d_cur <= 6:
            score += (d_to_opp - d_cur) * 2  # move away when close

        if best is None or score > best_score or (score == best_score and (dx, dy) != (0, 0) and best == (0, 0)):
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best