def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return [dx if abs(tx - x) >= abs(ty - y) else 0, dy if abs(ty - y) > abs(tx - x) else 0]

    # Deterministic tie-breaking order: prefer diagonal? keep consistent with deltas order.
    best_move = [0, 0]
    best_score = -10**18

    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        my_best = -10**18
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # Winning race if we are closer; also prefer closer overall.
            # Add small bias toward resources far from opponent to reduce denier success.
            dist_pen = my_d + (1 if (rx, ry) in obstacles else 0)
            win_term = (op_d - my_d) * 10
            far_bias = cheb(ox, oy, rx, ry) * 0.1
            score = win_term - dist_pen + far_bias
            if score > my_best:
                my_best = score

        # If multiple moves tie, choose the one that reduces our distance to the best target next.
        if my_best > best_score:
            best_score = my_best
            best_move = [dx0, dy0]
        elif my_best == best_score and best_move == [0, 0]:
            best_move = [dx0, dy0]

    return best_move