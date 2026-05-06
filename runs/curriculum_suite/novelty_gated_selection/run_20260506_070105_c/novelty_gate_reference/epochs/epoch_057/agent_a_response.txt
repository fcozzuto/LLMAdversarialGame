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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def best_step(posx, posy, target):
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = clamp(posx + dx, 0, w - 1), clamp(posy + dy, 0, h - 1)
            if (nx, ny) in obstacles:
                continue
            d = man((nx, ny), target)
            if d < best[0]:
                best = (d, dx, dy)
        if best[0] == 10**9:
            return 0, 0
        return best[1], best[2]

    best_move = (0, 0)
    best_score = -10**18

    # Limit targets for speed/determinism: choose top few by potential interference.
    target_candidates = sorted(
        resources,
        key=lambda t: (man((ox, oy), t) - man((sx, sy), t), -man((sx, sy), t)),
        reverse=True,
    )[:6]

    for t in target_candidates:
        # Approximate opponent greedy move toward t.
        odx, ody = best_step(ox, oy, t)
        nox, noy = clamp(ox + odx, 0, w - 1), clamp(oy + ody, 0, h - 1)
        opp_after = man((nox, noy), t)

        for dx, dy in dirs:
            nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
            if (nx, ny) in obstacles:
                continue
            self_after = man((nx, ny), t)
            if (nx, ny) == t:
                score = 10**6 + (opp_after - self_after)
            else:
                score = (opp_after - self_after) - 0.001 * man((nx, ny), (ox, oy))
            if score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]