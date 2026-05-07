def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_toward(tx, ty):
        dx = tx - sx
        dy = ty - sy
        mdx = 1 if dx > 0 else (-1 if dx < 0 else 0)
        mdy = 1 if dy > 0 else (-1 if dy < 0 else 0)
        nx, ny = sx + mdx, sy + mdy
        if inb(nx, ny):
            return [mdx, mdy]
        # fallback: best neighbor reducing cheb to target
        best = None
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if best is None or d < best[0] or (d == best[0] and (mx, my) < best[1]):
                best = (d, (mx, my))
        return [best[1][0], best[1][1]] if best else [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        return step_toward(cx, cy)

    best_res_for_me = None
    best_score = None
    for rx, ry in resources:
        dm = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # prefer resources I'm at least not behind on; strongly avoid far-behind
        if dm <= do:
            score = (dm - do) * 100 + dm
        else:
            score = (dm - do) * 100 + dm + 10000
        if best_score is None or score < best_score or (score == best_score and (rx, ry) < best_res_for_me):
            best_score = score
            best_res_for_me = (rx, ry)

    # Resource-denier: if opponent is essentially next to a resource, try to contest it
    closest_to_opp = None
    closest_opp_d = None
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if closest_opp_d is None or d < closest_opp_d or (d == closest_opp_d and (rx, ry) < closest_to_opp):
            closest_opp_d = d
            closest_to_opp = (rx, ry)

    if closest_opp_d is not None:
        my_d = cheb(sx, sy, closest_to_opp[0], closest_to_opp[1])
        # contest if we can arrive as fast or nearly as fast, else head to our best
        if my_d <= closest_opp_d + 1 and closest_opp_d <= 2:
            return step_toward(closest_to_opp[0], closest_to_opp[1])

    return step_toward(best_res_for_me[0], best_res_for_me[1])