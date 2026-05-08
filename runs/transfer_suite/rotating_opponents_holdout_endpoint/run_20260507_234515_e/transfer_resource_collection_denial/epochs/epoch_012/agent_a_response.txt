def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_obj(px, py):
        if not resources:
            return 0.0
        best = -10**18
        for rx, ry in resources:
            sd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Primary: prefer resources we can arrive earlier at (and by more).
            # Secondary: avoid giving opponent big advantage.
            # Tertiary: prefer closer target to accelerate.
            key = (od - sd) * 1000 + (-sd) * 10 + (od) * 1
            if key > best:
                best = key
        return best

    # If we are on a resource, stay (collect) deterministically.
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        v = step_obj(nx, ny)
        # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying.
        if v > best_val or (v == best_val and (abs(dx), abs(dy), dx == 0 and dy == 0) < (abs(best_move[0]), abs(best_move[1]), best_move[0] == 0 and best_move[1] == 0)):
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]