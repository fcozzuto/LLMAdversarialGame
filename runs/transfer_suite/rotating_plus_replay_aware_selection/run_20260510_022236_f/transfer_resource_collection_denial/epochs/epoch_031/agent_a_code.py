def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        try:
            x, y = p
            blocked.add((int(x), int(y)))
        except:
            pass

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def parse_xy(p):
        if isinstance(p, dict):
            if "position" in p:
                q = p["position"]
                return int(q[0]), int(q[1])
            for k in ("x", "X"):
                if k in p and "y" in p:
                    return int(p[k]), int(p["y"])
            if "coord" in p:
                q = p["coord"]
                return int(q[0]), int(q[1])
        return int(p[0]), int(p[1])

    parsed = []
    for r in resources:
        try:
            rx, ry = parse_xy(r)
            if inb(rx, ry) and (rx, ry) not in blocked:
                parsed.append((rx, ry))
        except:
            pass

    if not parsed:
        candidates = [(dx, dy) for dx, dy in moves if inb(sx+dx, sy+dy) and (sx+dx, sy+dy) not in blocked]
        for dx, dy in candidates:
            nx, ny = sx+dx, sy+dy
            if abs(nx-ox)+abs(ny-oy) >= abs(sx-ox)+abs(sy-oy):
                return [dx, dy]
        dx, dy = min(candidates, key=lambda t: (t[0]**2 + t[1]**2, t[0], t[1])) if candidates else (0, 0)
        return [int(dx), int(dy)]

    tx, ty = min(parsed, key=lambda p: (abs(p[0]-sx)+abs(p[1]-sy), abs(p[0]-ox)+abs(p[1]-oy), p[0], p[1]))
    vx = 1 if tx > sx else (-1 if tx < sx else 0)
    vy = 1 if ty > sy else (-1 if ty < sy else 0)

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx+dx, sy+dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d_self = abs(nx-tx) + abs(ny-ty)
        d_opp = abs(nx-ox) + abs(ny-oy)
        toward = abs(dx-vx) + abs(dy-vy)
        score = (d_self, -d_opp, toward, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]