def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in obstacles
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def obs_pen(x, y):
        p = 0
        for dx, dy in adj8:
            if (x + dx, y + dy) in obstacles:
                p += 1
        return p

    def greedy_opponent_step():
        if not resources:
            tx, ty = w - 1, h - 1
            best = (10**9, 10**9, 0, 0)
            for dx, dy in moves:
                nx, ny = ox + dx, oy + dy
                if not valid(nx, ny): continue
                key = (man(nx, ny, tx, ty), obs_pen(nx, ny), abs(nx - sx) + abs(ny - sy))
                if key < best[:3]:
                    best = (key[0], key[1], dx, dy)
            return (ox + best[2], oy + best[3])
        best = (10**9, 10**9, 0, 0)
        tx_best = None
        for rx, ry in resources:
            if tx_best is None or man(ox, oy, rx, ry) < man(ox, oy, tx_best[0], tx_best[1]):
                tx_best = (rx, ry)
        tx, ty = tx_best
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not valid(nx, ny): continue
            key = (man(nx, ny, tx, ty), obs_pen(nx, ny), -man(nx, ny, sx, sy))
            if key < best[:3]:
                best = (key[0], key[1], dx, dy)
        return (ox + best[2], oy + best[3])

    predicted_ox, predicted_oy = greedy_opponent_step()
    my_best = None
    my_resources = resources if resources else []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if my_resources:
            # Choose a resource that I can reach soon and that the opponent is unlikely to reach soon.
            best_for_move = None
            for rx, ry in my_resources:
                myd = man(nx, ny, rx, ry)
                opd = man(predicted_ox, predicted_oy, rx, ry)
                # Large penalty if opponent is closer; small penalty for obstacles; slight bias to reduce myd.
                key = (opd - myd, myd, obs_pen(nx, ny), man(nx, ny, ox, oy))
                if best_for_move is None or key > best_for_move[0]:
                    best_for_move = (key, (rx, ry))
            key = (-(best_for_move[0][0]), best_for_move[0][1], best_for_move[0][2], best_for_move[0][3], abs(dx) + abs(dy))
        else:
            # No resources: stabilize by moving away from opponent while avoiding obstacles.
            key = (-(man(nx, ny, ox, oy)), obs_pen(nx, ny), man(nx, ny, w - 1, h - 1), abs(dx) + abs(dy))
        if my_best is None or key < my_best[0]:
            my_best = (key, dx, dy)
    return [my_best[1], my_best[2]] if my_best else [0, 0]