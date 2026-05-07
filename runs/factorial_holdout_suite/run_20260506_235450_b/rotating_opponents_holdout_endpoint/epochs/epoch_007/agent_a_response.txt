def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx = 1 if ox < sx else (-1 if ox > sx else 0)
        ty = 1 if oy < sy else (-1 if oy > sy else 0)
        return [int(tx), int(ty)]

    def cheb_dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best_val = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy

        # Choose move that maximizes chance to be first: minimize (self_dist - opp_dist)
        # plus a small bias to reduce our distance overall.
        best_for_move = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            self_d = cheb_dist((nx, ny), (rx, ry))
            opp_d = cheb_dist((ox, oy), (rx, ry))
            # lower is better; make it deterministic via tuple ordering
            val = (self_d - opp_d, self_d, abs(rx - ox) + abs(ry - oy), rx, ry)
            if best_for_move is None or val < best_for_move:
                best_for_move = val

        # Convert to a comparable "higher is better" score
        cur = (-best_for_move[0], -best_for_move[1], -best_for_move[2])
        if best_val is None or cur > best_val:
            best_val = cur
            best_move = [int(nx - sx), int(ny - sy)]

    return best_move