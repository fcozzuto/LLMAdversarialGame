def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not inb(sx, sy) or (sx, sy) in obs:
        sx, sy = 0, 0

    moves = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def best_move(targets, mode):
        best_score = -10**18
        best = (0, 0)
        for ddx, ddy in moves:
            nx, ny = sx + ddx, sy + ddy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            if not targets:
                d = abs(nx - ox) + abs(ny - oy)
                score = (-d if mode == "chase" else d)
            else:
                dmin = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
                dopp = abs(nx - ox) + abs(ny - oy)
                if mode == "resource":
                    score = (-dmin * 10) + (-dopp)  # go to resources, avoid getting too close to opponent
                else:
                    score = (-abs(nx - ox) - abs(ny - oy) * 10)  # fallback
            if score > best_score:
                best_score = score
                best = (ddx, ddy)
        return [best[0], best[1]]

    if resources:
        return best_move(resources, "resource")
    return best_move([], "chase")