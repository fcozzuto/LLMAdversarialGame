def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = (observation.get("self_role") or "").lower()
    i_am_evader = "evad" in sr

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax + ay

    moves = [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
    def corner_score(px, py):
        return min(man(px, py, cx, cy) for cx, cy in corners)

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        d = man(nx, ny, ox, oy)
        # pursuer: reduce distance, also aim to push opponent into corners indirectly
        # evader: increase distance, also avoid giving pursuer easy cornering
        if i_am_evader:
            key = (-d, corner_score(nx, ny), nx, ny)
        else:
            key = (d, corner_score(ox, oy), -nx, -ny)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        # try stay or minimal fallback
        return [0, 0]
    return [int(best[0]), int(best[1])]