def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(p) for p in (observation.get("resources", []) or [])]
    if not resources:
        tx, ty = (w - 1, h - 1) if (w - 1, h - 1) not in obstacles else (0, h - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        best = (None, -10**9)
        for mx, my in candidates:
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                score = -abs(tx - nx) - abs(ty - ny)
                if score > best[1] or (score == best[1] and (mx, my) < best[0] if best[0] is not None else True):
                    best = ((mx, my), score)
        if best[0] is None:
            return [0, 0]
        return [best[0][0], best[0][1]]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    targets = sorted(resources, key=lambda t: (t[0], t[1]))
    my_near = min(targets, key=lambda t: (man(sx, sy, t[0], t[1]), t[0], t[1]))
    opp_near = min(targets, key=lambda t: (man(ox, oy, t[0], t[1]), t[0], t[1]))

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        dm_my = man(nx, ny, my_near[0], my_near[1])
        dm_opp = man(ox, oy, my_near[0], my_near[1])
        d_o = man(nx, ny, opp_near[0], opp_near[1])
        dopp_near = man(ox + (1 if mx == 1 else -1 if mx == -1 else 0), oy + (1 if my == 1 else -1 if my == -1 else 0), opp_near[0], opp_near[1]) if False else dm_opp

        # If we're behind, prioritize moving to deny by also increasing opponent distance to our target.
        lead = man(sx, sy, my_near[0], my_near[1]) - man(ox, oy, my_near[0], my_near[1])
        if lead <= 0:
            score = (dm_opp - dm_my) * 4 - dm_my + (d_o - dm_my)
        else:
            score = (dm_opp - dm_my) * 6 - dm_my - d_o

        if score > best_score or (score == best_score and (mx, my) < best_move):
            best_score = score
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]