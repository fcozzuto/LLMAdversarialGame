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
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def neigh_obs(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                c += 1
        return c

    best = None
    best_val = None
    best_2 = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, ox, oy)
        if is_evader:
            wall = 1 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 0
            ocount = neigh_obs(nx, ny)
            # maximize distance; then prefer hugging wall; then avoid clustered obstacles
            val = (d, wall, -ocount)
        else:
            # minimize distance; then prefer reducing both axis differences; then prefer fewer nearby obstacles
            axis = abs(nx - ox) + abs(ny - oy)
            ocount = neigh_obs(nx, ny)
            val = (-d, -axis, -ocount)
        if best is None or val > best_val:
            best = [dx, dy]
            best_val = val
    return best if best is not None else [0, 0]