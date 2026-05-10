def choose_move(observation):
    w = int(observation.get("grid_width", 1) or 1)
    h = int(observation.get("grid_height", 1) or 1)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = observation.get("resources", None)
    res_list = []
    if isinstance(resources, list):
        for p in resources:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    res_list.append((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("evad" not in self_role and "purs" in opp_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        ax = x1 - x2
        ay = y1 - y2
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    def nearest_resource_dist(x, y):
        if not res_list:
            return None
        best = None
        for rx, ry in res_list:
            d = man(x, y, rx, ry)
            if best is None or d < best:
                best = d
        return best

    best_move = [0, 0]
    bestv = -10**18 if pursuer else -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d_opp = man(nx, ny, ox, oy)
        d_res = nearest_resource_dist(nx, ny)
        wall = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
        if pursuer:
            v = (-d_opp) * 1000 + (-d_res if d_res is not None else 0) * 10 + wall * 0.5
        else:
            v = (d_opp) * 1000 + (-d_res if d_res is not None else 0) * 10 + wall * 0.1
        if v > bestv or (v == bestv and (dx, dy) < (best_move[0], best_move[1])):
            bestv = v
            best_move = [dx, dy]

    return best_move if best_move else [0, 0]