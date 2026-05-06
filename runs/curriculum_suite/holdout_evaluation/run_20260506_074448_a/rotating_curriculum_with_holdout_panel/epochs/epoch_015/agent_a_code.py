def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_list:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass
    if not resources:
        return [0, 0]

    opp = observation.get("opponent_position") or (None, None)
    ox, oy = opp[0], opp[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_target = None
    best_d = 10**9
    obs_set = set((p[0], p[1]) for p in resources)
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry) if ox is not None else 10**9
        # Bias toward targets we are closer to than opponent, but still greedy.
        if d < best_d - 1 or (d == best_d and od <= cheb(sx, sy, resources[0][0], resources[0][1])):
            best_d = d
            best_target = (rx, ry)
    tx, ty = best_target

    best_move = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Higher is better: prefer immediate pickup, then reducing distance, slight preference to block opponent.
        val = -nd
        if (nx, ny) in obs_set:
            val += 100000
        if ox is not None and (nx, ny) == (ox, oy):
            val -= 10000
        best = cheb(nx, ny, tx, ty)
        if ox is not None:
            od = cheb(ox, oy, tx, ty)
            val += 5 if best < od else 0
        if val > best_val or (val == best_val and best_move is None):
            best_val = val
            best_move = (dx, dy)
    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]