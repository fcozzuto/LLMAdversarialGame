def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None
    opp_par = (ox + oy) & 1

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # choose the resource that maximizes our "lead" after the move
        my_best = -10**9
        for tx, ty in resources:
            dm = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            # lead > 0 means we are closer (or will arrive sooner)
            lead = (do - dm)
            # small bias to earlier in-distance and away from opponent's immediate line
            line_pen = 0.35 if (tx == ox and abs(ty - oy) <= 2) else 0.0
            my_best = max(my_best, lead - 0.18 * dm - line_pen)

        # disrupt diagonal probing by preferring opposite parity from opponent
        parity_bonus = 0.25 if ((nx + ny) & 1) != opp_par else 0.0

        # obstacle "pressure": prefer moves that increase distance to nearest obstacle
        min_obs = 10**9
        for ox0, oy0 in obstacles:
            d = abs(nx - ox0) + abs(ny - oy0)
            if d < min_obs:
                min_obs = d
        obs_bonus = 0.10 * min_obs if min_obs < 4 else 0.0

        score = my_best + parity_bonus + obs_bonus
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]