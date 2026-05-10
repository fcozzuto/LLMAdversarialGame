def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = p
        obstacles.add((x, y))

    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    opp_adj = (abs(ox - sx) <= 1 and abs(oy - sy) <= 1 and (ox, oy) != (sx, sy))

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cells = []
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            cells.append((dx, dy, nx, ny))

    def nearest_unclaimed_dist(x, y):
        if not unclaimed:
            # fallback to center / enemy pressure
            cx, cy = w // 2, h // 2
            return min(abs(x - cx) + abs(y - cy), abs(x - ox) + abs(y - oy))
        best = 10**9
        for ux, uy in unclaimed:
            d = abs(x - ux) + abs(y - uy)
            if d < best: best = d
        return best

    cur_du = nearest_unclaimed_dist(sx, sy)
    opp_du = nearest_unclaimed_dist(ox, oy)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in cells:
        val = 0
        if (nx, ny) in self_t:
            val += 2.0
        if (nx, ny) in unclaimed:
            val += 3.5
        if (nx, ny) in opp_t:
            # flip only when it helps to reach unclaimed; otherwise avoid counterclaim
            nu = nearest_unclaimed_dist(nx, ny)
            if nu < cur_du:
                val += 2.2 + (cur_du - nu) * 0.7
            else:
                val -= 4.2
        # avoid getting too close to opponent when we can't improve unclaimed access
        nu = nearest_unclaimed_dist(nx, ny)
        val += (cur_du - nu) * 0.9
        val -= 0.15 * (abs(nx - ox) + abs(ny - oy))
        if opp_adj and (nx, ny) not in unclaimed and (nx, ny) not in self_t:
            val -= 1.8
        # slight bias toward moving away from opponent if we are not improving
        if (cur_du - nu) <= 0:
            val += 0.2 * (abs(sx - ox) + abs(sy - oy) - (abs(nx - ox) + abs(ny - oy)))
        # keep a mild deterministic preference order
        val -= 0.001 * (dx * 3 + dy)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]