def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def ok(x, y):
        return (x, y) not in obstacles

    # If no resources: run from opponent but avoid obstacles
    best_move = [0, 0]
    best_score = -10**18
    cur_r = 10**9
    cur_o = man(sx, sy, ox, oy)
    if resources:
        cur_r = min(man(sx, sy, rx, ry) for rx, ry in resources)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or not ok(nx, ny):
            continue
        o_dist = man(nx, ny, ox, oy)
        if resources:
            r_dist = min(man(nx, ny, rx, ry) for rx, ry in resources)
            # Prefer getting closer to resources, and staying farther from opponent.
            # Penalize moves that help opponent catch up (distance shrinks too much).
            delta_r = cur_r - r_dist
            delta_o = o_dist - cur_o
            # Also slightly prefer moves that reduce x/y spread to approach useful paths
            center_bias = -0.02 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
            score = (5.0 * delta_r) + (0.6 * o_dist) + (0.3 * max(0, delta_o)) - (0.9 * max(0, -delta_o)) + center_bias
        else:
            # After resources, keep maximizing opponent distance and avoid moving toward their likely direction
            score = (1.2 * o_dist) - 0.1 * man(nx, ny, w - 1 - sx, h - 1 - sy)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move