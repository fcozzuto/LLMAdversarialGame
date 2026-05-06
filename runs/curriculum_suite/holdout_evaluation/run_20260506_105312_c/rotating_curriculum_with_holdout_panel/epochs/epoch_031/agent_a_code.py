def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose target resource deterministically: nearest to us; tie -> lowest coordinates
    best_r = None
    best_d = 10**9
    for r in resources:
        rx, ry = r[0], r[1]
        d = cheb(sx, sy, rx, ry)
        if d < best_d or (d == best_d and (rx, ry) < (best_r[0], best_r[1]) if best_r else True):
            best_d = d
            best_r = (rx, ry)

    rx, ry = best_r
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        my_d = cheb(nx, ny, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        # Maximize: get closer while also preventing being left behind by opponent
        score = (best_d - my_d) * 10 - (my_d - op_d)
        # Small deterministic bias for staying near our target
        score += -my_d
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]