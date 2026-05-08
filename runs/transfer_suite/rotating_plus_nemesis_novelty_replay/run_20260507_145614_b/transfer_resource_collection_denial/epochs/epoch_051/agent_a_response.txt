def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    for r in resources:
        if (sx, sy) == (r[0], r[1]):
            return [0, 0]

    def dist(a, b, x, y):
        dx = a - x
        if dx < 0:
            dx = -dx
        dy = b - y
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    free_neighbors = []
    for dxi, dyi in moves:
        nx, ny = sx + dxi, sy + dyi
        cnt = 0
        for ex, ey in moves:
            xx, yy = nx + ex, ny + ey
            if inb(xx, yy):
                cnt += 1
        free_neighbors.append(cnt)

    best_target = None
    best_adv = -10**9
    best_selfd = 10**9
    for r in resources:
        rx, ry = r[0], r[1]
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        adv = od - sd  # positive means we're closer
        if adv > best_adv or (adv == best_adv and sd < best_selfd):
            best_adv, best_selfd, best_target = adv, sd, (rx, ry)

    tx, ty = best_target
    best = (-10**18, -10**18)
    best_move = (0, 0)

    for i, (dxi, dyi) in enumerate(moves):
        nx, ny = sx + dxi, sy + dyi
        if not inb(nx, ny):
            continue
        self_d = dist(nx, ny, tx, ty)
        opp_d = dist(ox, oy, tx, ty)

        # Also consider the best remaining resource from this candidate.
        # Keep it local/cheap: evaluate top few by current advantage.
        cand_best = -10**18
        for r in resources:
            rx, ry = r[0], r[1]
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            val = (od - sd) * 100 - sd  # prioritize increasing lead; then approach
            if val > cand_best:
                cand_best = val
                if cand_best > 10**7:
                    break

        mobility = free_neighbors[i]
        tie_center = -abs(nx - (w - 1) // 2) - abs(ny - (h - 1) // 2)

        score = cand_best + self_d * -1 + opp_d * 0 + mobility + tie_center
        key = (score, -self_d)
        if key > best:
            best = key
            best_move = (dxi, dyi)

    return [best_move[0], best_move[1]]