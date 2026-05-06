def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            key = (man(nx, ny, tx, ty), nx, ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    resources2 = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources2.append((x, y))
    if not resources2:
        return [0, 0]

    def best_target_for(px, py):
        best_adv = None
        best_closest = None
        for tx, ty in resources2:
            our_d = man(px, py, tx, ty)
            opp_d = man(ox, oy, tx, ty)
            adv = opp_d - our_d
            cand_adv = (adv, -our_d, tx, ty)
            if best_adv is None or cand_adv > best_adv:
                best_adv = cand_adv
            cand_close = (-our_d, tx, ty)
            if best_closest is None or cand_close > best_closest:
                best_closest = cand_close
        if best_adv[0] >= 0:
            return (best_adv[2], best_adv[3], best_adv[0], -best_adv[1])
        tx, ty = best_closest[1], best_closest[2]
        return (tx, ty, man(ox, oy, tx, ty) - man(px, py, tx, ty), man(px, py, tx, ty))

    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        tx, ty, adv, our_d = best_target_for(nx, ny)
        # Prefer higher advantage; tie-break by smaller distance to reduce dithering.
        key = (-adv, our_d, man(nx, ny, ox, oy), nx, ny)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    return [best_move[1], best_move[2]] if best_move else [0, 0]