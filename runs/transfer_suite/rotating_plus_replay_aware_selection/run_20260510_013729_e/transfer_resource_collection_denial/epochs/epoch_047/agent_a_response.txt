def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}
    cand = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_list = resources
    best_key = None
    best_move = [0, 0]

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # If engine would keep us in place due to obstacle, reflect that in scoring
        if (nx, ny) in obst:
            nx, ny = sx, sy

        ds_min = None
        lead_best = -10**9
        cap_best = 0
        for rx, ry in res_list:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds
            if ds_min is None or ds < ds_min:
                ds_min = ds
            if (nx, ny) == (rx, ry):
                cap_best = 1
                if lead > lead_best:
                    lead_best = lead
            else:
                if lead > lead_best:
                    lead_best = lead

        # Encourage resource capture, being ahead, and reducing distance to that target
        cap_bonus = 20 if cap_best else 0
        key = (cap_bonus, lead_best, -(ds_min if ds_min is not None else 0), -cheb(nx, ny, ox, oy), -(dx*3+dy))
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move