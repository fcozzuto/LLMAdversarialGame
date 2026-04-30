def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(w // 2, h // 2)]

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def nearest_dist(x, y):
        md = 10**9
        for tx, ty in resources:
            d = cheb(x, y, tx, ty)
            if d < md: md = d
        return md
    def best_greedy_step(px, py):
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if not valid(nx, ny):
                continue
            d = nearest_dist(nx, ny)
            key = (d, abs(dx) + abs(dy), 0)
            if d < best[0]:
                best = (d, dx, dy)
            elif d == best[0]:
                if abs(dx) + abs(dy) < abs(best[1]) + abs(best[2]):
                    best = (d, dx, dy)
        return best[1], best[2]

    my_best = (10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # simulate opponent greedy response
        odx, ody = best_greedy_step(ox, oy)
        nox, noy = ox + odx, oy + ody
        my_d = nearest_dist(nx, ny)
        op_d = nearest_dist(nox, noy)

        # prioritize getting closer; also try to worsen opponent's prospects
        score = my_d - 0.75 * op_d
        # tie-break deterministically toward smaller chebyshev and then toward staying
        tie = (my_d, -op_d, abs(dx), abs(dy))
        cur_best_tie = (my_best[0], 0, 0, 0)
        if score < my_best[0] or (score == my_best[0] and tie < cur_best_tie):
            my_best = (score, dx, dy)

    return [int(my_best[1]), int(my_best[2])]