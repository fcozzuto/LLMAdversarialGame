def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_list = observation.get("obstacles") or []
    obs = set()
    for p in obs_list:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res_list = observation.get("resources") or []
    resources = []
    for r in res_list:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    t = int(observation.get("turn_index", 0))
    rot = t % 9
    order = moves[rot:] + moves[:rot]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        bestv = -10**18
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources where we are closer; add tiebreakers for determinism.
            v = (do - ds) * 1000 - ds * 3 + (rx + 31 * ry) * 0.000001
            if v > bestv:
                bestv = v
                best = (rx, ry)
        tx, ty = best

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        ds = man(nx, ny, tx, ty)
        do = man(ox, oy, tx, ty)
        # Keep moving toward target; if opponent is much closer to the target, try to reduce distance anyway.
        score = -ds * 10 + (do - ds) * 1
        # Avoid stepping onto squares that are "behind" in both coordinates relative to target.
        if (nx - tx) * (sx - tx) > 0 and (ny - ty) * (sy - ty) > 0:
            score -= 2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]