def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources_list = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    res = set((p[0], p[1]) for p in resources_list)
    obs = set((p[0], p[1]) for p in obstacles_list)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Immediate pickup if possible
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res and (nx, ny) not in obs:
            return [dx, dy]

    if not resources_list:
        return [0, 0]

    # One-step lookahead: evaluate each feasible move by best resource "advantage"
    best = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if (nx, ny) in res:
            return [dx, dy]
        move_score = -10**9
        # Deterministic iteration over resources
        for rx, ry in sorted(res):
            sd = dist8(nx, ny, rx, ry)
            od = dist8(ox, oy, rx, ry)
            # Prefer resources where we get there first; tie-break by being closer to the resource
            advantage = od - sd
            tie = -(sd + 0.01 * (rx + 3 * ry))
            val = (advantage, tie)
            if val > (move_score, move_score):
                move_score = val[0]  # keep consistent scalar compare below
                # use tuple compare separately by storing best tuple
                best_tuple = val
        # compute a final comparable tuple for the move
        # recompute best tuple more directly for correctness with scalar shortcut above
        best_tuple = (-10**9, -10**9)
        for rx, ry in sorted(res):
            sd = dist8(nx, ny, rx, ry)
            od = dist8(ox, oy, rx, ry)
            val = (od - sd, -(sd + 0.01 * (rx + 3 * ry)))
            if val > best_tuple:
                best_tuple = val
        if best is None or best_tuple > best:
            best = best_tuple
            best_move = [dx, dy]

    return best_move