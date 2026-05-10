def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    xp, yp = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [0, 0]
    xo, yo = int(op[0]), int(op[1])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    myt = to_set("self_territory")
    opt = to_set("opponent_territory")

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def unclaimed_near(x, y):
        cnt = 0
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-2, -1, 0, 1, 2):
                nx, ny = x + dx, y + dy
                if (abs(dx) + abs(dy)) <= 2 and (nx, ny) in unclaimed:
                    cnt += 1
        return cnt

    def obstacle_near(x, y):
        cnt = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) in obstacles:
                cnt += 1
        return cnt

    for dx, dy in moves:
        nx, ny = xp + dx, yp + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0.0

        if (nx, ny) in unclaimed:
            score += 60.0
        if (nx, ny) in myt:
            score += 14.0
        if (nx, ny) in opt:
            score -= 65.0

        score += 2.5 * unclaimed_near(nx, ny)

        d_opp = abs(nx - xo) + abs(ny - yo)
        score += 0.8 * d_opp  # favor not being close to counterclaimers

        d_me = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        score -= 0.03 * d_me

        score -= 2.2 * obstacle_near(nx, ny)

        if dx == 0 and dy == 0:
            score -= 1.5  # prefer movement when possible

        if score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score and best is not None:
            if (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]