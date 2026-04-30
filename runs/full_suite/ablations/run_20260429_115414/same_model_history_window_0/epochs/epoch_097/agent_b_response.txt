def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mdist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Target selection: prefer resources we can reach as fast or faster than opponent.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        my_d = mdist((sx, sy), (rx, ry))
        op_d = mdist((ox, oy), (rx, ry))
        if my_d <= op_d:
            sc = 1000 - 10*my_d + 5*(op_d - my_d)
        else:
            sc = 400 - 8*my_d + 2*(op_d - my_d)  # chase only if nothing better
        if best is None or sc > best[0]:
            best = (sc, rx, ry, my_d, op_d)

    # If no resources, drift toward center while keeping away from opponent.
    if best is None:
        tx, ty = (w-1)//2, (h-1)//2
    else:
        tx, ty = best[1], best[2]

    # Choose move that improves distance to target and increases separation from opponent.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_to_target = mdist((nx, ny), (tx, ty))
        my_to_opp = mdist((nx, ny), (ox, oy))
        # Slight preference for not stepping into immediate opponent vicinity.
        val = -my_to_target + 0.6*my_to_opp
        # Tie-break: prefer moving closer (or equal) to target.
        if best is not None and my_to_target == best[3]:
            val += 2
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]