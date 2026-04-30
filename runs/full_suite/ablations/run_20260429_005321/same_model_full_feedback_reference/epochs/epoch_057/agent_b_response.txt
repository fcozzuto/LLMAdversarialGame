def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            score = d2(nx, ny, ox, oy) - d2(nx, ny, w / 2, h / 2)
            if score > best[0]:
                best = (score, dx, dy)
        return [int(best[1]), int(best[2])]

    # Target resources where opponent is currently closer; try to steal/block.
    best_dx, best_dy = 0, 0
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        my_gain = -10**18
        for rx, ry in resources:
            sd = d2(nx, ny, rx, ry)
            od = d2(ox, oy, rx, ry)

            # Prefer resources where we are getting relatively closer than opponent is.
            # Also add a small term to reduce distance to opponent when contesting (deny pickup zones).
            contest = od - sd
            deny = -abs(sd - od)

            s = contest * 10 + deny
            if (rx, ry) == (nx, ny):
                s += 10**6
            if s > my_gain:
                my_gain = s

        # Small tie-break: prefer staying farther from opponent to avoid getting pushed off contested resources.
        final = my_gain + 0.1 * d2(nx, ny, ox, oy)
        if final > best_score:
            best_score = final
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]