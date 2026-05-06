def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # pick best contested target: maximize opp advantage; tie-break toward nearer target
    best = None
    best_key = None
    for cx, cy in resources:
        sd = cheb(sx, sy, cx, cy)
        od = cheb(ox, oy, cx, cy)
        key = (od - sd, -sd, -cx, -cy)
        if best_key is None or key > best_key:
            best_key = key
            best = (cx, cy)

    tx, ty = best

    # If we are already closer (or equal), go for nearest; otherwise intercept by moving toward the target cell
    # that minimizes our distance to the target while increasing opponent distance to it.
    # This is a deterministic local policy (no pathfinding).
    self_ahead = cheb(sx, sy, tx, ty) <= cheb(ox, oy, tx, ty)

    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        # Primary objective differs depending on whether we are ahead
        if self_ahead:
            # collect: minimize distance to target; also avoid giving opponent advantage too quickly
            d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            score = (-d, -(opp_d - d))
        else:
            # contested: move to reduce our distance to target while making opponent worse (by limiting our approach angle)
            d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            score = (-d, (d - opp_d), -nx, -ny)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move