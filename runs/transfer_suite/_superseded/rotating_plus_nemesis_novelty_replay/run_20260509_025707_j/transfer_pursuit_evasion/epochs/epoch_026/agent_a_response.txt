def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    if w < 2 or h < 2 or not isinstance(sp, (list, tuple)) or not isinstance(op, (list, tuple)) or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    role = (observation.get("self_role") or "pursuer").lower()
    is_evader = role == "evader"

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not is_evader:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        best = (10**9, 10**9, 0, 0)
        for ddx, ddy in deltas:
            nx, ny = sx + ddx, sy + ddy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            sc = cheb(nx, ny, ox, oy)
            md = abs(nx - ox) + abs(ny - oy)
            t = (sc, md, ddx, ddy)
            if t < best: best = t
        return [best[2], best[3]]

    corners = [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]
    target = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    tx, ty = target

    best = (-10**9, -10**9, -10**9, 0, 0)
    for ddx, ddy in deltas:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, ox, oy)
        md = abs(nx - ox) + abs(ny - oy)
        corner_adv = -(abs(nx - tx) + abs(ny - ty))
        # Prefer more distance, then more manhattan distance, then nearer to target corner, then deterministic tiebreak.
        key = (d, md, corner_adv, -ddx, -ddy)
        if key > best:
            best = key
    return [best[3], best[4]]