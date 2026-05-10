def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_need_from(px, py):
        best_need = -10**9
        best_dist = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            dS = cheb(px, py, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            need = dO - dS
            if need > best_need or (need == best_need and dS < best_dist):
                best_need, best_dist = need, dS
        return best_need, best_dist

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        need, dS = best_need_from(nx, ny)
        # Prefer contesting when possible; otherwise minimize own distance.
        val = need * 1000 - dS
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if cheb(nx, ny, ox, oy) < cheb(sx, sy, ox, oy):
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]