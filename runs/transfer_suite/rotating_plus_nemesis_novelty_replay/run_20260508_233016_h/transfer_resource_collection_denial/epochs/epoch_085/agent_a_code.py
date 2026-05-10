def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = {tuple(p) for p in obs_list}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Deterministic tie-break ordering
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_target = None
    best_key = None
    for rx, ry in resources:
        me = cheb(sx, sy, rx, ry)
        op = cheb(ox, oy, rx, ry)
        slack = op - me
        # Prefer targets we can beat (slack>=0). Otherwise, prefer least-worse ones.
        if slack >= 0:
            key = (-1, -slack, me, rx, ry)  # first element ranks "beatable"
        else:
            # Penalize being slower strongly but still allow progress when all are contested
            key = (0, -(slack), me + (me - op), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    def blocked(x, y):
        return (x, y) in obstacles

    # Local move selection with opponent-aware evaluation
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        my_d = cheb(nx, ny, tx, ty)
        op_d = cheb(ox, oy, tx, ty)
        # Prefer: reaching target sooner, and ensuring we're not worse than opponent
        beat = op_d - my_d  # higher is better
        # Small secondary: avoid increasing distance to target too much
        cur_d = cheb(sx, sy, tx, ty)
        dist_improve = cur_d - my_d
        # Deterministic combined key: maximize beat, then maximize dist_improve, then lex move
        val = (-(-beat), -(-dist_improve), dx, dy)  # convert to "min" key style
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]