def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))
    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if resources:
        opp_target = min(resources, key=lambda t: (man(ox, oy, t[0], t[1]), t[0], t[1]))
    else:
        opp_target = (sx, sy)

    best = None
    for dx, dy, nx, ny in moves:
        d_to_opp_t = man(nx, ny, opp_target[0], opp_target[1])
        d_to_opp = man(nx, ny, ox, oy)
        if resources:
            min_d_res = min(man(nx, ny, rx, ry) for rx, ry in resources)
            min_d_opp_res = min(man(ox, oy, rx, ry) for rx, ry in resources)
        else:
            min_d_res = 0
            min_d_opp_res = 0

        # Intercept: prefer closing distance to opponent's nearest target,
        # while not letting us lag far behind that target compared to opponent.
        lead_term = (min_d_opp_res - d_to_opp_t)
        score = (3.0 * lead_term) + (0.4 * min_d_res) - (0.25 * d_to_opp)

        key = (-score, dx, dy, nx, ny)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]