def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Prefer resources where we have an advantage; if none, take the closest safe one.
    best_t = None
    best_key = None
    for x, y in resources:
        d_me = cheb(sx, sy, x, y)
        d_op = cheb(ox, oy, x, y)
        adv = d_op - d_me  # larger is better
        key = (-adv, d_me, abs(x - ox) + abs(y - oy), x, y)
        # Transform to minimize: want highest adv -> minimize -adv; then smaller d_me.
        if best_key is None or key < best_key:
            best_key = key
            best_t = (x, y)

    tx, ty = best_t
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if desired_dx == 0 and desired_dy == 0:
        return [0, 0]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Choose best among candidate moves (prioritize moving toward target; if blocked, try alternates).
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_after = cheb(nx, ny, tx, ty)
        d_opp_after = cheb(ox, oy, tx, ty)
        # Score: primarily minimize our distance; secondarily maximize relative pressure (opp advantage).
        score = (d_after, -(d_opp_after - d_after), abs(nx - ox) + abs(ny - oy), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]