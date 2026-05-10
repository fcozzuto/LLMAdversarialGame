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

    self_territory = observation.get("self_territory") or []
    opp_territory = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    self_set = set()
    for p in self_territory:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            self_set.add((int(p[0]), int(p[1])))
    opp_set = set()
    for p in opp_territory:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            opp_set.add((int(p[0]), int(p[1])))
    unclaimed_set = set()
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            unclaimed_set.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inside(x, y) and (x, y) not in obs

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    best_sc = None

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        edge = 1 if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1) else 0
        d_self_c = man(nx, ny, cx, cy)
        d_opp_c = man(ox, oy, cx, cy)
        d_opp = man(nx, ny, ox, oy)

        if (nx, ny) in opp_set:
            flip_bonus = 14.0
        elif (nx, ny) in unclaimed_set:
            flip_bonus = 4.0
        elif (nx, ny) in self_set:
            flip_bonus = 1.0
        else:
            flip_bonus = 2.0

        # Prefer moving toward center and away from opponent; prioritize immediate flips.
        sc = (
            flip_bonus
            + (d_opp_c - d_self_c) * 0.9
            + (d_opp) * 0.08
            - edge * 0.6
        )

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]