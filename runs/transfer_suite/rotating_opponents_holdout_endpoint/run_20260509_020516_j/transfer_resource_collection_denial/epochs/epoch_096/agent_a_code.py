def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    def pget(key, default):
        try:
            p = observation.get(key, default)
            return int(p[0]), int(p[1])
        except:
            return default

    sx, sy = pget("self_position", [0, 0])
    ox, oy = pget("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        try:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for t in observation.get("resources") or []:
        try:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    opponent_denier = (observation.get("opponent_role") == "resource_denier")

    best = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd  # positive means we are closer
        # Against denier, slightly favor resources that are closer to us even if we can't "win"
        if opponent_denier:
            score = (adv, -sd, -rx, -ry)
        else:
            score = (adv, -sd, -rx, -ry)
        if best is None or score > best[0]:
            best = (score, rx, ry)

    _, tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Choose move that minimizes our distance to target, avoids obstacles, tie-breaks with opponent distance.
    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_to = md(nx, ny, tx, ty)
        d_opp = md(nx, ny, ox, oy)
        # If denier, also avoid allowing opponent to grab target next: prefer moves that increase their distance to target.
        opp_to = md(ox, oy, tx, ty)
        opp_next_to = md(ox, oy, tx, ty)
        cand = (d_to, -d_opp, -opp_next_to, dx, dy)
        if best_move is None or cand < best_move[0]:
            best_move = (cand, dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]