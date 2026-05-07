def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if w <= 0 or h <= 0 or not resources:
        return [0, 0]

    moves = [(-1, 0), (0, 1), (1, 0), (0, -1), (-1, 1), (1, 1), (-1, -1), (1, -1), (0, 0)]

    def dist(ax, ay, bx, by):
        return max(abs(bx - ax), abs(by - ay))

    best_move = (0, 0)
    best_key = None
    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        local_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            st = dist(nsx, nsy, rx, ry)
            ot = dist(ox, oy, rx, ry)
            # Prefer resources we can arrive at no later than opponent; otherwise minimize lateness.
            advantage = ot - st
            if st <= ot:
                key = (1, advantage, -st, rx, ry)
            else:
                key = (0, advantage, -st, rx, ry)
            if local_best is None or key > local_best:
                local_best = key

        if local_best is None:
            continue
        # Maximize local_best; deterministic move ordering for ties.
        if best_key is None or local_best > best_key:
            best_key = local_best
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]