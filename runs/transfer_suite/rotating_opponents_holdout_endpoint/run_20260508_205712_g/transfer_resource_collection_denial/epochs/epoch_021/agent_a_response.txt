def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Target selection: maximize our relative closeness vs opponent; tie-break for closer-to-self
    best_key = None
    target = resources[0]
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # advantage positive means we are closer/equal
        key = (opd - myd, -myd, -abs(rx - sx) - abs(ry - sy), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            target = (rx, ry)

    tx, ty = target

    # One-step obstacle-aware greedy move
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_to = cheb(sx, sy, tx, ty)
    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        # Prefer reducing distance; small preference for moving away from opponent when race is tight
        oppd = cheb(ox, oy, nx, ny)
        score = (-(d), (oppd - cheb(ox, oy, tx, ty)), - (abs(nx - tx) + abs(ny - ty)))
        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    # If all candidate moves were blocked, stay
    if best is None:
        return [0, 0]
    # Ensure we don't do worse only when already adjacent: otherwise allow slight improvement
    if cheb(sx + best_move[0], sy + best_move[1], tx, ty) > cur_to + 1:
        return [0, 0]
    return best_move