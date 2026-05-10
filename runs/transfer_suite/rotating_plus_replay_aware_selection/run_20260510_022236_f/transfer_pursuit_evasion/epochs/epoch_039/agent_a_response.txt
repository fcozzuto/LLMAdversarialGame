def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def wall_dist(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)

    def neigh_block_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) == (ox, oy):
                continue
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                c += 1
            elif (nx, ny) in obs:
                c += 1
        return c

    best = None
    best_move = (0, 0)

    cur_ddx, cur_ddy = sx - ox, sy - oy
    cur_d2 = cur_ddx * cur_ddx + cur_ddy * cur_ddy

    # Deterministic scoring: maximize for evader, minimize for pursuer.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        ndx, ndy = nx - ox, ny - oy
        d2 = ndx * ndx + ndy * ndy

        # Capture check: only relevant if pursuer
        if nx == ox and ny == oy:
            if not is_evader:
                return [dx, dy]

        # Obstacle pressure / mobility
        block = neigh_block_count(nx, ny)
        wd = wall_dist(nx, ny)

        # Additional bias: keep moving in direction away/towards opponent, prefer staying nearer open center for evader.
        dir_score = 0
        if is_evader:
            # prefer increase in distance; avoid moving closer
            dir_score = (d2 - cur_d2)
            # avoid hugging walls (lower wall_dist), and prefer less blocked neighborhoods
            score = (dir_score * 1000) + (wd * 10) - (block * 25)
        else:
            # prefer decrease in distance; also prefer routes that keep us away from walls and with fewer blocks
            dir_score = (cur_d2 - d2)
            score = (dir_score * 1000) + (wd * 3) - (block * 15)

        # Deterministic tie-break by move order; first best wins.
        if best is None:
            best = score
            best_move = (dx, dy)
        else:
            if is_evader:
                if score > best:
                    best = score
                    best_move = (dx, dy)
            else:
                if score > best:
                    best = score
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]