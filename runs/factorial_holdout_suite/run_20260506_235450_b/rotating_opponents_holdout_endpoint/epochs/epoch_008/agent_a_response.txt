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
        dx = 1 if ox < sx else (-1 if ox > sx else 0)
        dy = 1 if oy < sy else (-1 if oy > sy else 0)
        return [int(dx), int(dy)]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
        # Minimize advantage loss: prefer moves where we are closer (relative to opponent) to some resource.
        best_for_this_move = None
        nearest_d = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            self_d = cheb((nx, ny), (rx, ry))
            opp_d = cheb((ox, oy), (rx, ry))
            key = (self_d - opp_d, self_d, rx, ry)
            if best_for_this_move is None or key < best_for_this_move:
                best_for_this_move = key
            if nearest_d is None or self_d < nearest_d:
                nearest_d = self_d
        # Secondary: if equal advantage, go toward nearest resource, then prefer cardinal/diagonal deterministically by move index.
        move_key = (best_for_this_move, nearest_d, dx, dy)
        if best is None or move_key < best:
            best = move_key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]