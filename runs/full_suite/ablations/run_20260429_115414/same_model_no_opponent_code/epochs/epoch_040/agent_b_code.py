def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            score = d - (1 if dx == 0 and dy == 0 else 0)
            if score > best[2]:
                best = (dx, dy, score)
        return [best[0], best[1]]

    best_target = resources[0]
    best_score = -10**18
    side = 1 if sx <= (w - 1) // 2 else -1
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we're not behind the opponent; also prefer pushing toward far side.
        closer_bonus = 6 if do > ds else 0
        behind_pen = 3 if do < ds else 0
        far_side = 2 if ((rx - (w - 1) // 2) * side) > 0 else 0
        opp_pressure = 4 if do == 1 or (do == 0) else 0
        score = (do - ds) + closer_bonus + far_side + opp_pressure - behind_pen - 0.2 * ds
        if score > best_score:
            best_score = score
            best_target = (rx, ry)

    tx, ty = best_target
    cur_d = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_mscore = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d1 = cheb(nx, ny, tx, ty)
        # If opponent can steal next, slightly reduce such moves by keeping distance to opponent.
        dop = cheb(nx, ny, ox, oy)
        reduce = cur_d - d1
        mscore = 10 * reduce - 0.8 * d1 + 0.4 * (dop - cheb(sx, sy, ox, oy))
        # Small tie-break toward progress in x then y for determinism.
        if dx == 0 and dy == 0:
            mscore -= 0.5
        if dx != 0:
            mscore += 0.01 * dx
        if dy != 0:
            mscore += 0.002 * dy
        if mscore > best_mscore:
            best_mscore = mscore
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]