def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def clamp(x, a, b):
        return a if x < a else (b if x > b else x)

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target():
        if not resources:
            return (ox, oy)
        best = None
        best_key = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            key = (myd - 0.9 * oppd, myd, -rx, -ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = best_target()

    def move_eval(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        nd = cheb(nx, ny, tx, ty)
        # Prefer reaching our chosen target, while keeping some distance from opponent.
        base = -nd
        opdist = cheb(nx, ny, ox, oy)
        base += 0.06 * opdist
        # Discourage stepping into the opponent's immediate neighborhood when target ties.
        base -= 0.25 if opdist <= 1 else 0.0
        # Slight preference to move (avoid dithering) unless it blocks obstacles.
        base -= 0.01 * (1 if (nx, ny) != (sx, sy) else 0)
        return base

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        val = move_eval(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]