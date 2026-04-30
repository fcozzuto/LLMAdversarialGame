def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = observation["resources"]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    deltas = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]
    best_target = None
    best_val = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        val = (ds - do, ds, rx, ry)  # prefer resources we are closer to
        if best_val is None or val < best_val:
            best_val = val
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]

    tx, ty = best_target
    signx = 1 if tx > sx else (-1 if tx < sx else 0)
    signy = 1 if ty > sy else (-1 if ty < sy else 0)
    priority = [(signx, signy), (signx, 0), (0, signy), (-signx, signy), (signx, -signy), (-signx, 0), (0, -signy), (0, 0)]

    best_move = (0, 0)
    best_score = None
    for dx, dy in priority + deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # tie-break with staying safer (prefer not moving away from "we are ahead" target race)
        do = cheb(ox, oy, tx, ty)
        score = (d - do, d, -abs(nx - sx) - abs(ny - sy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]