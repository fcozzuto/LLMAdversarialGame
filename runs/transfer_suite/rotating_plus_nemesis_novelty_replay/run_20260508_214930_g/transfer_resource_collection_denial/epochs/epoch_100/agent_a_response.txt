def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def clamp_move(nx, ny):
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return sx, sy
        if (nx, ny) in obstacles:
            return sx, sy
        return nx, ny

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # Target scoring: prefer resources where we are not behind; if behind, prefer least-behind.
    best_move = (0, 0)
    best_score = -10**18

    # Precompute opponent distances (chebyshev gives good proxy with diagonal moves).
    oppd = {}
    for rx, ry in resources:
        oppd[(rx, ry)] = cheb((ox, oy), (rx, ry))

    for dx, dy in moves:
        nx, ny = clamp_move(sx + dx, sy + dy)
        # Evaluate best target the move would contest.
        my_now = (nx, ny)
        move_score = -10**18
        for rx, ry in resources:
            d_my = cheb(my_now, (rx, ry))
            d_op = oppd[(rx, ry)]
            # Being closer than opponent is dominant (resource-denier friendly).
            contest = d_op - d_my  # positive means we are closer
            # Bias toward actual pickup (smaller distance), and toward earlier contest.
            pickup_bias = -d_my
            tie_bias = -(rx * 3 + ry) * 1e-6
            val = 1000 * contest + 5 * pickup_bias + tie_bias
            if val > move_score:
                move_score = val
        # Mild preference to progress (avoid stalling if any resource reachable).
        prog = -cheb((ox, oy), (nx, ny)) * 0.01
        total = move_score + prog
        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]