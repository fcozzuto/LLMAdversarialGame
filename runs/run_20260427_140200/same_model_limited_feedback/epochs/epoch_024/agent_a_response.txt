def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def step_ok(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2): 
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_res = None
    best_val = -10**9
    best_dist = 10**9
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = od - sd  # prefer resources we're closer to
        if val > best_val or (val == best_val and sd < best_dist):
            best_val = val
            best_dist = sd
            best_res = (rx, ry)

    if best_res is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_res

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(nx, ny, ox, oy)
        # primary: get closer to target; secondary: keep distance from opponent
        score = (-sd2) + 0.05 * od2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]