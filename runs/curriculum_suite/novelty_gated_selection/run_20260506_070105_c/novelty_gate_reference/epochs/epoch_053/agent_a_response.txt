def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        ax = a - c
        if ax < 0:
            ax = -ax
        ay = b - d
        if ay < 0:
            ay = -ay
        return ax + ay

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = (0, 0)
    bestv = -10**18

    # Contest opponent's likely sweep row: resources on oy get a strong bonus.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        cur_best = -10**18
        for rx, ry in resources:
            if (rx, ry) == (nx, ny):
                val = 10**9
            else:
                sd = md(nx, ny, rx, ry)
                od = md(ox, oy, rx, ry)
                lead = od - sd  # positive means we are closer
                row_bonus = 6 if ry == oy else 0
                col_bonus = 2 if rx == ox else 0
                block_bonus = 2 if (ry == oy and rx == ox) else 0
                # Encourage reaching something we can win soon, not just the absolute closest.
                val = lead * 3 + row_bonus + col_bonus + block_bonus - sd * 0.3
            if val > cur_best:
                cur_best = val

        # Small tie-break: prefer moves that reduce distance to opponent to limit their sweep.
        opp_tie = -md(nx, ny, ox, oy) * 0.01
        v = cur_best + opp_tie
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]