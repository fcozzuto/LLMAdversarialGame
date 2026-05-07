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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    valid = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                valid.append((x, y))
    if not valid:
        return [0, 0]

    best = None
    for tx, ty in valid:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # If we can win: minimize (sd - od), then sd.
        # If we can't: maximize delay (od - sd), then prioritize smaller od to deny sooner.
        if sd < od:
            score = (0, sd - od, sd, tx, ty)
        else:
            score = (1, -(od - sd), od, tx, ty)
        if best is None or score < best[0]:
            best = (score, (tx, ty))

    tx, ty = best[1]
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [int(dx), int(dy)]