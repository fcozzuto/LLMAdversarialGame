def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(obstacles)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(px, py):
        return 0 <= px < w and 0 <= py < h and (px, py) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    rem = []
    for rx, ry in resources:
        if valid(rx, ry):
            rem.append((rx, ry))

    best_move = [0, 0]
    best_val = -10**18

    if rem:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            dres = min(cheb(nx, ny, rx, ry) for (rx, ry) in rem)
            dob = cheb(nx, ny, ox, oy)
            val = (-dres * 10) + (dob * 0.5)
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        # No resources known: move toward center while keeping distance from opponent.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            distc = abs(nx - cx) + abs(ny - cy)
            dob = cheb(nx, ny, ox, oy)
            val = (-distc) + dob * 0.2
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move