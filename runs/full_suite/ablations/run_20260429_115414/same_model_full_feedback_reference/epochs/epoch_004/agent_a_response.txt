def choose_move(observation):
    W = observation["grid_width"]
    H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs_set = set((p[0], p[1]) for p in obstacles)
    res_set = set((p[0], p[1]) for p in resources)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def mindist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def legal(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obs_set:
            return False
        return True

    def score_cell(nx, ny):
        if (nx, ny) in obs_set or not inb(nx, ny):
            return -10**9

        # Encourage immediate pickup.
        s = 0
        if (nx, ny) in res_set:
            s += 100000

        # Resource pressure: prefer cells where we are closer than the opponent to many resources.
        for rx, ry in resources:
            myd = mindist2(nx, ny, rx, ry)
            opd = mindist2(ox, oy, rx, ry)
            # If we can get there first (or tie), good; if opponent already closer, bad.
            s += (opd - myd) * 2

            # If opponent can capture this resource next move (from its immediate neighbors), penalize.
            if max(abs(ox - rx), abs(oy - ry)) == 1:
                # But if we step onto it now, already handled.
                if (rx, ry) != (nx, ny):
                    s -= 60000 // (1 + myd)

        # Avoid positions adjacent to opponent unless we are picking up.
        if max(abs(nx - ox), abs(ny - oy)) == 1 and (nx, ny) not in res_set:
            s -= 80000

        # Slightly prefer staying away from opponent when not collecting, but keep some mobility.
        s -= mindist2(nx, ny, ox, oy) // 4

        # Prefer moves that keep us not stuck: count available neighboring legal cells.
        cnt = 0
        for dx, dy in moves:
            tx, ty = nx + dx, ny + dy
            if legal(tx, ty) or (tx == nx and ty == ny):
                if (tx, ty) not in obs_set and inb(tx, ty):
                    cnt += 1
        s += cnt * 3

        return s

    best_dx, best_dy = 0, 0
    best_score = -10**18

    # Deterministic tie-breaking order: moves list order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        sc = score_cell(nx, ny)
        if sc > best_score:
            best_score = sc
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]