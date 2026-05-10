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

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = set(tuple(map(int, c)) for c in (observation.get("unclaimed_cells") or []) if isinstance(c, (list, tuple)) and len(c) == 2)
    self_set = set(tuple(map(int, p)) for p in self_terr if isinstance(p, (list, tuple)) and len(p) == 2)
    opp_set = set(tuple(map(int, p)) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) == 2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        if (nx, ny) in opp_set:
            gain = 5.0
        elif (nx, ny) in unclaimed:
            gain = 2.0
        elif (nx, ny) in self_set:
            gain = 0.6
        else:
            gain = 0.9
        center_pen = 0.25 * (abs(nx - cx) + abs(ny - cy))
        contest_pen = 0.08 * man(nx, ny, ox, oy)
        sc = gain - center_pen - contest_pen
        if best is None or sc > best:
            best = sc
            best_move = [dx, dy]

    return best_move