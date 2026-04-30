def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    obs_set = set((a, b) for a, b in obstacles)

    def clamp(p, lo, hi):
        return lo if p < lo else hi if p > hi else p

    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # No resources: move to farthest corner from opponent while staying valid
        best = None
        for dx, dy in deltas:
            nx = clamp(x + dx, 0, w - 1)
            ny = clamp(y + dy, 0, h - 1)
            if (nx, ny) in obs_set:
                continue
            d_op = dist(nx, ny, ox, oy)
            key = (d_op, -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2), -dx, -dy)
            if best is None or key > best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx = clamp(x + dx, 0, w - 1)
        ny = clamp(y + dy, 0, h - 1)
        if (nx, ny) in obs_set:
            continue

        # Target resource that maximizes "denial": how much closer we are than opponent
        move_best = -10**18
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            denial = (do - ds)  # positive means we are closer
            s = denial * 100 - ds  # prioritize denial, then speed
            if s > move_best:
                move_best = s

        # Tie-breakers: prefer moves that reduce distance to nearest resource
        if move_best > best_score:
            best_score = move_best
            best_move = [dx, dy]
        elif move_best == best_score:
            # lexicographic tie-break favoring diagonal progress then towards opponent's side less (avoid mirroring)
            # Compute nearest self resource distance for tie
            def nearest_dist(px, py):
                md = 10**9
                for rx, ry in resources:
                    d = dist(px, py, rx, ry)
                    if d < md:
                        md = d
                return md
            cand_nd = nearest_dist(nx, ny)
            cur_nd = nearest_dist(x + best_move[0], y + best_move[1])
            if cand_nd < cur_nd or (cand_nd == cur_nd and (dx, dy) < (best_move[0], best_move[1])):
                best_move = [dx, dy]

    return best_move