def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_set.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        cx, cy = w // 2, h // 2
        best = (None, -10**9)
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            score = -cheb(nx, ny, cx, cy) + 0.15 * cheb(nx, ny, ox, oy)
            if score > best[1]:
                best = ((dx, dy), score)
        return [best[0][0], best[0][1]]

    # Choose resource: prefer one we can reach first; else maximize our relative advantage.
    best_res = None
    best_val = -10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # First-arrival preference, then closeness, then stable tie-break by position.
        val = (1000000 if sd <= od else 0) + (od - sd) * 1000 - sd
        val += (rx * 17 + ry * 31) * 1e-6
        if val > best_val:
            best_val = val
            best_res = (rx, ry)

    rx, ry = best_res
    best_move = (0, 0)
    best_score = -10**18

    # Move greedily toward chosen resource while not walking into the opponent too aggressively.
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dist_to_res = cheb(nx, ny, rx, ry)
        opp_dist = cheb(nx, ny, ox, oy)
        # If we can step onto a resource, do it.
        on_res = 1 if (nx, ny) == (rx, ry) else 0
        score = on_res * 10**6 + (-dist_to_res) * 100 + (opp_dist) * 0.5
        # Prefer not increasing our race disadvantage too much.
        cur_sd = cheb(sx, sy, rx, ry)
        cur_od = cheb(ox, oy, rx, ry)
        new_sd = cheb(nx, ny, rx, ry)
        new_od = cheb(ox, oy, rx, ry)
        score += (cur_od - cur_sd) * 5 + (new_od - new_sd) * 5
        # Strongly avoid stepping away from the resource.
        if dist_to_res > cheb(sx, sy, rx, ry) + 1:
            score -= 50
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]