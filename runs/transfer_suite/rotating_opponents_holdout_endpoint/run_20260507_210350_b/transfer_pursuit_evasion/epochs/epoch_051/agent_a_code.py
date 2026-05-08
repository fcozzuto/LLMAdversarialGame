def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    rolestr = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in rolestr for k in ("evader", "escape", "flee", "runner"))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def min_obs_dist(x, y):
        if not obstacles: return 10
        best = 10
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best: best = d
        return best

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # deterministic corner target: farthest from opponent (evader), nearest (pursuer)
    if is_evader:
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    else:
        tx, ty = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best_score = -10**9
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        d_op = cheb(nx, ny, ox, oy)
        d_corner = cheb(nx, ny, tx, ty)
        d_obs = min_obs_dist(nx, ny)

        # score shaping
        if is_evader:
            score = (d_op * 100) - (d_corner * 2) + (d_obs * 3)
        else:
            score = (-d_op * 100) - (d_corner * 2) + (d_obs * 3)

        # tie-break deterministically: prefer staying only if equal
        if score > best_score or (score == best_score and (dx, dy) == (0, 0)):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]