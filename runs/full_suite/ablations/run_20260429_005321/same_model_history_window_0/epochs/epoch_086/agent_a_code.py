def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"] or []
    obstacles = set(tuple(p) for p in (observation["obstacles"] or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    if not resources:
        tx, ty = (w-1)//2, (h-1)//2
    else:
        best = None
        for r in resources:
            rx, ry = r
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources where we are closer; break ties by absolute closeness and then by position
            score = (do - ds, -ds, -rx, -ry)
            if best is None or score > best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dx_best, dy_best = 0, 0
    best_tuple = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = dist((nx, ny), (tx, ty))
        d_opp = dist((ox, oy), (tx, ty))
        # Also discourage moving away from opponent's relative pressure
        press = d_opp - d_self
        tup = (press, -d_self, -abs(nx - tx) - abs(ny - ty), -dx, -dy)
        if best_tuple is None or tup > best_tuple:
            best_tuple = tup
            dx_best, dy_best = dx, dy

    return [int(dx_best), int(dy_best)]