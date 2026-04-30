def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # prefer resources where we are closer; otherwise still pick something useful
            lead = do - ds
            score = lead * 1000 - ds * 3 + (-abs(rx - ox) - abs(ry - oy))
            if best is None or score > best[0] or (score == best[0] and (rx, ry) < best[1]):
                best = (score, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1 - ox + sx) // 2, (h - 1 - oy + sy) // 2
        if tx < 0: tx = 0
        if ty < 0: ty = 0
        if tx >= w: tx = w - 1
        if ty >= h: ty = h - 1

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        ds_n = cheb(nx, ny, tx, ty)
        ds_now = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # value: get closer to target; also preserve/extend lead vs opponent
        lead_now = do - ds_now
        lead_n = do - ds_n
        opp_dist = cheb(nx, ny, ox, oy)
        val = (lead_n - lead_now) * 500 + (ds_now - ds_n) * 20 + opp_dist * 1 - ds_n * 2
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]