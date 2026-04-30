def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(map(tuple, observation["obstacles"]))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = (0, 0, -1)  # (dist_to_opponent_negative, dist_to_center, move_index)
        target_x, target_y = w // 2, h // 2
        moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        for i, (dx, dy) in enumerate(moves):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h: 
                continue
            if (nx, ny) in obstacles:
                continue
            d_op = cheb(nx, ny, ox, oy)
            d_ct = cheb(nx, ny, target_x, target_y)
            cand = (-d_op, d_ct, -i)
            if best == (0, 0, -1) or cand > best:
                best = cand
        dx, dy = moves[-best[2]-1] if best[2] != -1 else (0, 0)
        return [dx, dy]

    tx, ty = min(resources, key=lambda p: (cheb(sx, sy, p[0], p[1]), p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)
        # Primary: get closer to target; Secondary: farther from opponent; Tertiary: deterministic move order
        key = (d_t, -d_o, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]