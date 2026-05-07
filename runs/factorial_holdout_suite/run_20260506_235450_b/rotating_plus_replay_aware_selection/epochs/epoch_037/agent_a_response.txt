def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []

    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Pick best resource by race advantage (opponent distance - my distance).
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds
        key = (lead, -ds, -do)  # highest lead; then closer; then further from opponent
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    best_move = None
    best_move_key = None
    for dx, dy, nx, ny in legal:
        ds_new = cheb(nx, ny, rx, ry)
        do_new = cheb(ox, oy, rx, ry)
        lead_new = do_new - ds_new
        # Prefer reducing distance to target; if tied, increase lead.
        key = (-ds_new, lead_new, -abs(ox - nx) - abs(oy - ny), dx, dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]