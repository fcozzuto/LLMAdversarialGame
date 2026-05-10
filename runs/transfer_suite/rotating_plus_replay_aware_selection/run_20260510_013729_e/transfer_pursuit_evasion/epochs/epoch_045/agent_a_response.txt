def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def obs_penalty(x, y):
        if not obs:
            return 0
        p = 0
        for bx, by in obs:
            d = abs(x - bx) + abs(y - by)
            if d == 0:
                p -= 1000000
            elif d == 1:
                p -= 6
            elif d == 2:
                p -= 2
        return p

    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny):
            if (nx, ny) not in obs:
                candidates.append((nx, ny, dx, dy))
    if not candidates:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny):
                candidates.append((nx, ny, dx, dy))

    best = None
    best_val = None
    for nx, ny, dx, dy in candidates:
        d = dist(nx, ny, ox, oy)
        diagonal = 1 if (dx != 0 and dy != 0) else 0
        approach = (dist(sx, sy, ox, oy) - d)
        if is_evader:
            val = d * 10 + diagonal * 0.5 + approach * 2 + obs_penalty(nx, ny)
        else:
            val = -d * 10 + diagonal * 0.5 + approach * 2 + obs_penalty(nx, ny)
        if best_val is None or (val > best_val):
            best_val = val
            best = [dx, dy]
    return [int(best[0]), int(best[1])]