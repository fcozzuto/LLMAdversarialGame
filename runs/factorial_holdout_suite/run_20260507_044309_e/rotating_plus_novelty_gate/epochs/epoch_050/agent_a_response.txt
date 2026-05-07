def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def md(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx + dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    resources = observation.get("resources", []) or []
    if not resources:
        tx, ty = w // 2, h // 2
        best = min(valid, key=lambda m: (md(m[2], m[3], tx, ty), dirs.index((m[0], m[1])) if (m[0], m[1]) in dirs else 0))
        return [best[0], best[1]]

    res = [tuple(r) for r in resources]
    # Best opponent target
    opp_idx = min(range(len(res)), key=lambda i: (md(ox, oy, res[i][0], res[i][1]), i))
    opp_t = res[opp_idx]

    # Decide whether to contest opponent's closest target
    my_to_opp_t = md(sx, sy, opp_t[0], opp_t[1])
    opp_to_opp_t = md(ox, oy, opp_t[0], opp_t[1])
    contest = (my_to_opp_t <= opp_to_opp_t)

    if contest:
        target = opp_t
    else:
        # Choose resource maximizing lead (opponent distance - ours); deterministic tie by index
        best_i = 0
        best_score = -10**9
        for i in range(len(res)):
            rx, ry = res[i]
            d_my = md(sx, sy, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            score = d_opp - d_my
            if score > best_score or (score == best_score and i < best_i):
                best_score = score
                best_i = i
        target = res[best_i]

    tx, ty = target
    best = min(valid, key=lambda m: (md(m[2], m[3], tx, ty), (m[0], m[1]) != (0, 0), m[0] + 2*m[1]))
    return [best[0], best[1]]