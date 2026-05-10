def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = obstacles_list if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick a resource we can beat, balancing (our advantage first) then efficiency.
    best = None
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        # Larger advantage is better; also avoid very long waits.
        key = (-(do - ds), ds + do, abs(rx - 3) + abs(ry - 3), rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), ds, do)
    tx, ty = best[1]

    # Choose move that reduces distance to target, prefers safety from obstacles,
    # and lightly accounts for opponent pressure on the same target.
    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = abs(tx - nx) + abs(ty - ny)

        # Next-step opponent distance after our move (opponent actually moves, but we approximate).
        # Favor positions that keep opponent relatively farther from the chosen target.
        d_opp = abs(tx - ox) + abs(ty - oy)

        # Obstacle proximity penalty to avoid getting stuck (simple local check).
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                x2, y2 = nx + ax, ny + ay
                if inb(x2, y2) and (x2, y2) in obstacles:
                    adj_obs += 1

        key = (d_self, adj_obs, -(d_opp - d_self), abs(dx) + abs(dy), dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, [dx, dy])

    if best_move is None:
        return [0, 0]
    return best_move[1]