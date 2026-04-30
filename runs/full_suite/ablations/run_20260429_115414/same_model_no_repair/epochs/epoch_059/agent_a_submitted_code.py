def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def obs_adj(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    if not resources:
        return [0, 0]

    # Pick a target resource where we have (or can gain) distance advantage.
    best = None
    for rx, ry in resources:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        if (rx, ry) in obstacles:
            continue
        # Prefer positive advantage and nearer to us; penalize unsafe (adjacent obstacles).
        key = ((od - sd), -sd, -(abs(rx - w // 2) + abs(ry - h // 2)), -obs_adj(rx, ry), rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    if best is None:
        return [0, 0]
    rx, ry = best[1]

    # Choose move maximizing expected advantage while avoiding obstacles-adjacent squares.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = manh(nx, ny, rx, ry)
        nod = manh(ox, oy, rx, ry)
        # Try to reduce our distance and keep/extend opponent deficit.
        val = (nod - nsd, -nsd, -obs_adj(nx, ny), -abs((nx - rx)) - abs((ny - ry)), nx, ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]