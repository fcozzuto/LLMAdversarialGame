def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position")
    op = observation.get("opponent_position")
    if w <= 0 or h <= 0 or not isinstance(sp, (list, tuple)) or not isinstance(op, (list, tuple)) or len(sp) < 2 or len(op) < 2:
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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x, y, a, b):
        dx = abs(x - a)
        dy = abs(y - b)
        return dx if dx > dy else dy
    def mindist_obs(x, y):
        if not obstacles:
            return 99
        best = 99
        for (ox2, oy2) in obstacles:
            d = abs(x - ox2) + abs(y - oy2)
            if d < best: best = d
            if best == 0: break
        return best

    # Score components: primary distance to opponent (min for pursuer, max for evader).
    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        blocked = (nx, ny) in obstacles
        dopp = cheb(nx, ny, ox, oy)
        dobs = mindist_obs(nx, ny)
        # Penalize stepping onto obstacle strongly (engine would keep still, but avoid it deterministically).
        obs_pen = 1000 if blocked else 0

        if is_evader:
            cand = (obs_pen, -dopp, -dobs, nx, ny)
        else:
            cand = (obs_pen, dopp, -dobs, nx, ny)

        if best is None or cand < best:
            best = cand
            best_move = [dx, dy]
    return best_move if isinstance(best_move, list) else [0, 0]