def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick the resource with maximum advantage = (opp time - self time).
    best = None
    best_adv = -10**9
    best_tieb = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        tieb = (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0), ds)
        if adv > best_adv or (adv == best_adv and tieb < best_tieb):
            best_adv = adv
            best = (rx, ry)
            best_tieb = tieb

    rx, ry = best
    # Greedy step toward target; if blocked, try alternatives that still reduce chebyshev distance.
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    curd = cheb(sx, sy, rx, ry)
    best_step = (0, 0)
    best_score = (curd, 10**9, 10**9)  # (dist, obstacle_pen, tie)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        hit = 1 if (nx, ny) in obstacles else 0
        nd = cheb(nx, ny, rx, ry)
        # Prefer strictly shorter; then avoid obstacles; then toward center; deterministic.
        score = (nd, hit, abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        if nd < curd:
            if score < best_score:
                best_score = score
                best_step = (dx, dy)
        else:
            if best_score[0] >= curd and score < best_score:
                best_score = score
                best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]