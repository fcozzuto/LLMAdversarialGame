def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    if not resources:
        for dx, dy in [(0,0),(1,1),(1,0),(0,1),(-1,1),(-1,0),(0,-1),(1,-1),(-1,-1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obs:
            continue
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        key = (od - sd, -sd, -((rx+ry) % 7))
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1] if best else (int(resources[0][0]), int(resources[0][1]))

    def step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    dx0, dy0 = step_toward(tx, ty)
    moves = [(dx0, dy0),(0, dy0),(dx0, 0),(dx0, -dy0),(-dx0, dy0),(0,0),(1,1),(1,0),(0,1),(-1,0),(0,-1),(-1,-1),(1,-1),(-1,1)]
    for dx, dy in moves:
        if dx not in (-1,0,1) or dy not in (-1,0,1):
            continue
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd_self = abs(tx - nx) + abs(ty - ny)
        nd_opp = abs(tx - ox) + abs(ty - oy)
        # slight preference: if opponent is also close to target, prefer reducing our distance
        if best and (nd_opp - nd_self, -nd_self) >= (nd_opp - (abs(tx - sx) + abs(ty - sy)), -(abs(tx - sx) + abs(ty - sy))):
            return [dx, dy]

    for dx, dy in [(dx0, dy0),(0,0),(1,0),(0,1),(-1,0),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            return [dx, dy]
    return [0, 0]