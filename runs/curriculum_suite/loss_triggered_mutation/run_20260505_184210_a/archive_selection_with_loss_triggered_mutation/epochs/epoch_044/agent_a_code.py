def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    res_list = sorted(resources, key=lambda p: (p[0] * 100 + p[1]))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate move by best target advantage
        worst = -10**18
        for rx, ry in res_list[:6]:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer taking a target where we are closer than opponent
            adv = od - sd
            # Slightly prefer moving up/forward in y to reach more area
            progress = (ry - ny)
            # Slightly avoid moving toward opponent (reduce their stealing options)
            dist_opp = cheb(nx, ny, ox, oy)
            score = adv * 1000 + progress * 3 + dist_opp * 2 - sd
            if score > worst:
                worst = score

        # If no positive advantage, still prioritize improving our distance to nearest resource
        nearest_d = min(cheb(nx, ny, rx, ry) for (rx, ry) in res_list)
        score2 = worst + (-nearest_d * 2)

        # Tie-break deterministically: deterministic ordering via lexicographic (dx,dy)
        if score2 > best_score or (score2 == best_score and (dx, dy) < best_move):
            best_score = score2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]