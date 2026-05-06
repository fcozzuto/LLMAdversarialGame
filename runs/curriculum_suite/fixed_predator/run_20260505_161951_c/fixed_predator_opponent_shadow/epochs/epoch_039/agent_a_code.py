def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        # Shadow-avoidance: move to increase distance from opponent while keeping toward center
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        best = None
        for dx, dy, nx, ny in moves:
            key = (-dist(nx, ny, ox, oy), dist(nx, ny, cx, cy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Pick a "race-winnable" resource; maximize (opp_dist - my_dist), prefer smaller my_dist
    best_t = None
    best_key = None
    for rx, ry in resources:
        md = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # If equal, still allow contest but slightly prefer resources closer to us
        key = (-(od - md), md, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    # For chosen target, choose move that reduces my distance and increases opponent distance to that cell
    best = None
    for dx, dy, nx, ny in moves:
        myd = dist(nx, ny, rx, ry)
        opd = dist(nx, ny, ox, oy) + dist(ox, oy, rx, ry)  # proxy: keep opp off our target route
        # Primary: improve (opponent distance to target - our distance) for target
        key = (-(dist(ox, oy, rx, ry) - myd), myd, opd, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]