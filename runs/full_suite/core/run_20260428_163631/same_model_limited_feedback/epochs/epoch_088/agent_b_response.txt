def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Race-target: prefer resources where we can arrive sooner than opponent, and that limit opponent's lead.
    best_resource = None
    best_val = None
    for rx, ry in resources:
        d_me = cheb(x, y, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Higher is better: big (op - me) lead; also slightly prefer closer overall.
        val = (d_op - d_me) * 10 - d_me
        if best_val is None or val > best_val or (val == best_val and (rx, ry) < best_resource):
            best_val = val
            best_resource = (rx, ry)

    tx, ty = best_resource

    # Choose best next move toward target while avoiding obstacles.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_me_next = cheb(nx, ny, tx, ty)
        d_op_to_target = cheb(ox, oy, tx, ty)

        # Encourage moves that improve relative race and avoid getting stuck near obstacles.
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if 0 <= px < w and 0 <= py < h and (px, py) in obstacles:
                    adj_obs += 1

        # Also favor moving closer immediately (small tie-break).
        score = (d_op_to_target - d_me_next) * 10 - d_me_next - adj_obs * 2

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]