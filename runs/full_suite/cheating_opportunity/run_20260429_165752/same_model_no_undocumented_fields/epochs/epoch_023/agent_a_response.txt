def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not moves:
        return [0, 0]

    if not resources:
        # No resources: deterministic move to reduce opponent mobility by going toward center-ish.
        tx, ty = w // 2, h // 2
        best = (0, 0)
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                nx, ny = sx, sy
            d = cheb(nx, ny, tx, ty)
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Evaluate each move by how much it improves our "distance advantage" to the nearest resource.
    def nearest_dist(x, y):
        md = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < md:
                md = d
        return md

    my_best = 10**9
    op_nearest = nearest_dist(ox, oy)
    chosen = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        my_nearest = nearest_dist(nx, ny)
        advantage = op_nearest - my_nearest  # higher is better (we become closer than opponent)
        # Tie-break: prefer smaller my_nearest, then lexicographically smaller move for determinism.
        if (advantage > (op_nearest - my_best)) or (advantage == (op_nearest - my_best) and (my_nearest < my_best)) or \
           (advantage == (op_nearest - my_best) and my_nearest == my_best and (dx, dy) < chosen):
            my_best = my_nearest
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]