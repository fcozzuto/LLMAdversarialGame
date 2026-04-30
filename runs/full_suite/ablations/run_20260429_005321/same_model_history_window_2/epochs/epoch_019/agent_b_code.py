def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    w = int(w); h = int(h)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_sc = -10**9
    best_move = [0, 0]
    for dx, dy in dirs:
        nx = sx + dx
        ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        d_to_res = min(cheb(nx, ny, rx, ry) for rx, ry in res)
        d_from_opp = cheb(nx, ny, ox, oy)
        cur_d_to_res = min(cheb(sx, sy, rx, ry) for rx, ry in res)
        improve = cur_d_to_res - d_to_res
        sc = improve * 10 + d_from_opp - d_to_res * 2
        if best is None or sc > best_sc:
            best_sc = sc
            best_move = [dx, dy]
    if best is None:
        return [0, 0]
    return best_move