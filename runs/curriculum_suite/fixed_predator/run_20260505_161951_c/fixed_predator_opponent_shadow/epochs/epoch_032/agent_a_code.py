def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    resources = [tuple(p) for p in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    if resources:
        tx, ty = min(resources, key=lambda p: man(sx, sy, p[0], p[1]))
    else:
        tx, ty = ox, oy

    best = None
    best_score = -10**18
    for dx, dy, nx, ny in moves:
        d = man(nx, ny, tx, ty)
        oppd = man(nx, ny, ox, oy)
        open_ct = 0
        for ddx, ddy in dirs:
            if ddx == 0 and ddy == 0:
                continue
            ex, ey = nx + ddx, ny + ddy
            if inb(ex, ey) and (ex, ey) not in obstacles:
                open_ct += 1
        score = (-d * 10) + (open_ct * 3) + (oppd * 0)
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return best