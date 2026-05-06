def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set(obstacles)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = observation.get("resources", [])
    if not resources:
        resources = [(max(0, min(w - 1, ox)), max(0, min(h - 1, oy)))]

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    best_move = (0, 0); best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = -cheb(nx, ny, sx, sy)  # discourage staying unless needed
        best_target = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer targets closer to us than opponent; also prefer overall closeness to us
            v = (do - ds) * 1000 - ds
            if v > best_target:
                best_target = v
        score += best_target
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if not valid(sx + dx, sy + dy):
        for ddx, ddy in dirs:
            if valid(sx + ddx, sy + ddy):
                return [ddx, ddy]
        return [0, 0]
    return [dx, dy]