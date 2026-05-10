def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    res_set = set((r[0], r[1]) for r in resources)

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Deterministically pick a target resource we can contest: maximize (opp_dist - self_dist),
    # tie-break by smaller self_dist and then lexicographic position.
    best_t = None
    best_adv = -10**18
    best_selfd = 10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and (sd < best_selfd or (sd == best_selfd and (rx, ry) < (best_t[0], best_t[1])))):
            best_adv = adv
            best_selfd = sd
            best_t = (rx, ry)

    tx, ty = best_t
    # One-step lookahead: choose move that improves contest on the chosen target,
    # while avoiding obstacles and lightly preferring immediate pickups.
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        pickup = 10**6 if (nx, ny) in res_set else 0
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        score = pickup + (opp_d - self_d) * 1000 - self_d

        # Secondary: if target not immediately reachable soon, still keep some structure toward it.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]