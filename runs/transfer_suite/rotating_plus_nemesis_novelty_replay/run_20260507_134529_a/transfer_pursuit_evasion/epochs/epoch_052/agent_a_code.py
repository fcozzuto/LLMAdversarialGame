def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    self_is_evader = "evader" in self_role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_cell(x, y):
        # distance metric
        d = abs(x - ox) + abs(y - oy)
        if not self_is_evader:
            base = 100 * (-d)
        else:
            base = 100 * (d)

        # avoid dead ends / low mobility
        mob = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                mob += 1
        base += (mob * (1 if self_is_evader else 0.5))

        # wall-running bias for evader: prefer hugging whichever wall is farther from opponent
        if self_is_evader:
            dist_left, dist_right = x, (w - 1 - x)
            dist_top, dist_bot = y, (h - 1 - y)
            wall_dist = max(dist_left, dist_right, dist_top, dist_bot)
            near_wall = 1 if (x in (0, w - 1) or y in (0, h - 1)) else 0
            base += near_wall * (5 + wall_dist * 0.2)

        # slight preference away from opponent corner traps when evading
        if self_is_evader:
            tx = min(x, w - 1 - x)
            ty = min(y, h - 1 - y)
            base += (tx + ty) * 0.2

        return base

    best = (sx, sy)
    best_val = score_cell(sx, sy)

    # Tie-break deterministically: prefer larger score, then moves closer to increasing/decreasing distance
    def tie_key(x, y):
        d = abs(x - ox) + abs(y - oy)
        return d if self_is_evader else -d

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = score_cell(nx, ny)
        if v > best_val:
            best_val = v
            best = (nx, ny)
        elif v == best_val:
            if tie_key(nx, ny) > tie_key(best[0], best[1]):
                best = (nx, ny)

    return [int(best[0] - sx), int(best[1] - sy)]