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

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or (role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def center_dist(x, y):
        ax = x - cx
        if ax < 0: ax = -ax
        ay = y - cy
        if ay < 0: ay = -ay
        return ax + ay

    # Prefer not to step onto/adjacent to obstacles when possible (deterministic)
    def obstacle_proximity(x, y):
        d = 0
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1), (1,1), (1,-1), (-1,1), (-1,-1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                d += 1
        return d

    best_move = (0, 0)
    if is_pursuer:
        # Reduce distance; slightly avoid running into corners if tied.
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            prox = obstacle_proximity(nx, ny)
            # Alignment: after move, match pursuer-evasion axis by nudging toward opponent relative sign
            align = 0
            if nx == ox: align = 1
            if ny == oy: align = 1
            key = (dist, prox, -align, center_dist(nx, ny), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]
    else:
        # Evader: maximize distance; prefer moving to reduce opponent's ability to approach by heading toward open space.
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            prox = obstacle_proximity(nx, ny)
            # Corner avoidance: stay away from edges unless it increases distance
            edge_pen = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
            # Higher is better for evader
            openness = edge_pen - prox
            # Bonus for increasing distance; discourage stationary if tied.
            stationary_pen = 1 if (dx == 0 and dy == 0) else 0
            key = (-dist, stationary_pen, -openness, center_dist(nx, ny), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]