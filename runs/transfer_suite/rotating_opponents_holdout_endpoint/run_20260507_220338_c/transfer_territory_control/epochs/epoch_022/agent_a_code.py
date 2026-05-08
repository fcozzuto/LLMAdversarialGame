def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    my = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    un = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    if (sx, sy) in obstacles:
        obstacles.discard((sx, sy))

    un_list = list(un)
    if not un_list:
        un_list = []

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    order = {d: i for i, d in enumerate(dirs)}

    cur_d = abs(sx - ox) + abs(sy - oy)
    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        is_un = (nx, ny) in un
        is_my = (nx, ny) in my
        is_opp = (nx, ny) in opp
        d_opp = abs(nx - ox) + abs(ny - oy)

        # heuristic: expand by claiming unclaimed; keep distance from opponent,
        # but allow flipping if it enters opponent territory.
        score = 0.0
        if is_un:
            score += 6.0
        if is_my:
            score += 2.0
        if is_opp:
            score += 4.5  # flipping on entry
            score += 0.1 * (d_opp - cur_d)  # mildly prefer capturing while not getting closer

        # prefer moving outward from opponent (safer expansion)
        score += 0.6 * d_opp

        # bias toward nearest unclaimed to keep pushing territory forward
        if un_list:
            md = 10**9
            limit = 18 if len(un_list) > 18 else len(un_list)
            for i in range(limit):
                ux, uy = un_list[i]
                dd = abs(nx - ux) + abs(ny - uy)
                if dd < md:
                    md = dd
            score += -0.25 * md

        # deterministic tie-breaker
        score_key = (score, order[(dx, dy)], nx, ny)
        best_key = (best_score, order[best_move], best_move[0] + sx, best_move[1] + sy)
        if score_key > best_key:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]