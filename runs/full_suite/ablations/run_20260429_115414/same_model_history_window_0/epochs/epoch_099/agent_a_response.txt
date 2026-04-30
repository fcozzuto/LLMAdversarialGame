def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]
    w = observation["grid_width"]
    h = observation["grid_height"]

    obs_set = {(p[0], p[1]) for p in obstacles}
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    def best_target():
        if not resources:
            return None
        best = None
        best_key = None
        for rx, ry in resources:
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            lead = sd - od  # prefer most negative (we closer than opponent)
            # Break ties deterministically: closer to us, then lexicographic
            key = (lead, sd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx_ty = best_target()

    # If we can't find a target, move away from opponent
    if tx_ty is None:
        best_move = (0, 0)
        best_val = None
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inside(nx, ny):
                continue
            val = -cheb(nx, ny, ox, oy)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        dx, dy = best_move
        return [dx, dy]

    tx, ty = tx_ty
    cur_d = cheb(x, y, tx, ty)

    # Primary: step that reduces distance to target; secondary: avoid moving into tight proximity if possible.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer reducing distance; if equal, prefer increasing distance from opponent.
        # Also discourage stagnation when another valid move improves us.
        stagn = 1 if (dx == 0 and dy == 0 and nd == cur_d) else 0
        score = (-(nd - cur_d), -stagn, cheb(nx, ny, ox, oy), -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]