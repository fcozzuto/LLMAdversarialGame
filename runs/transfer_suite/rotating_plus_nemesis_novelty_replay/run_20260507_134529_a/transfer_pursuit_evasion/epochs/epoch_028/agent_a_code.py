def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    res = observation.get("resources") or []
    res_pts = []
    for p in res:
        if p is not None and len(p) >= 2:
            res_pts.append((int(p[0]), int(p[1])))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx*dx + dy*dy

    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        if res_pts:
            d_res = min(dist2(nx, ny, rx, ry) for rx, ry in res_pts)
        else:
            d_res = 0
        v = d_res - 0.5 * d_opp
        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best