def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    self_set = set((int(p[0]), int(p[1])) for p in self_terr if isinstance(p, (list, tuple)) and len(p) == 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) == 2)
    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set((int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) == 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_move = (0, 0)
    for dx, dy in dirs:
        x, y = sx + dx, sy + dy
        if not inside(x, y) or (x, y) in obs:
            continue
        center_dist = abs(x - cx) + abs(y - cy)
        opp_dist = man(x, y, ox, oy)
        self_dist = man(x, y, sx, sy)

        if (x, y) in opp_set:
            score = 30.0
        elif (x, y) in self_set:
            score = 6.0
        elif (x, y) in un_set:
            score = 12.0
        else:
            score = 3.0

        score += 2.0 / (1.0 + opp_dist)  # punish being near opponent
        score += -0.6 * center_dist     # push toward center
        score += -0.05 * self_dist      # prefer forward progress
        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]