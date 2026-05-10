def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs_set = set((p[0], p[1]) for p in obstacles)
    res_list = [(r[0], r[1]) for r in resources]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_score(nx, ny):
        if (nx, ny) in obs_set:
            return -10**12
        if not res_list:
            # No resources visible: move toward center while keeping distance from opponent
            cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
            dcen = abs(nx - cx) + abs(ny - cy)
            dopp = manh(nx, ny, ox, oy)
            return -dcen + 0.01 * dopp

        best = -10**12
        for rx, ry in res_list:
            if (nx, ny) == (rx, ry):
                val = 10**9  # immediate collection
            else:
                our_d = manh(nx, ny, rx, ry)
                opp_d = manh(ox, oy, rx, ry)
                # Prefer taking resources that opponent is relatively far from; also prefer closeness to us
                val = 50 * (opp_d - our_d) - our_d
            if val > best:
                best = val
        # Soft obstacle avoidance: slight penalty for getting adjacent (Chebyshev)
        for ax, ay in obstacles:
            if max(abs(nx - ax), abs(ny - ay)) == 1:
                best -= 5
        return best

    best_move = [0, 0]
    best_val = -10**12
    # Deterministic tie-break by fixed dir order and then lexicographic delta
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = cell_score(nx, ny)
        if v > best_val or (v == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = v
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]