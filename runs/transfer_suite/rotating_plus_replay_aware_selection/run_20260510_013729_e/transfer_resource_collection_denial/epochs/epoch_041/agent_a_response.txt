def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}

    if not resources:
        return [0, 0]

    cand = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_set = set((x, y) for x, y in resources)

    def best_for_cell(x, y):
        # Score aims to stay closer (higher lead), then shorter distance,
        # and slightly prefer being farther from opponent overall unless it helps deny.
        best = None
        for rx, ry in resources:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds
            oppd = cheb(x, y, ox, oy)
            # Prefer immediate landing on a resource, then lead, then distance,
            # then deterministic resource ordering.
            cap = 2 if (x, y) == (rx, ry) else 0
            key = (cap, lead, -ds, -oppd, -(rx * 8 + ry))
            if best is None or key > best:
                best = key
        return best

    best_move = [0, 0]
    best_key = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        key = best_for_cell(nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move