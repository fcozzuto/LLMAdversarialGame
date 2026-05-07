def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def parse_xy(p):
        if isinstance(p, dict):
            if "position" in p:
                p = p["position"]
            elif "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
        return int(p[0]), int(p[1])

    obst = set()
    for p in obstacles:
        try:
            x, y = parse_xy(p)
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))
        except Exception:
            pass

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def king(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def cell_score(x, y):
        if (x, y) in obst:
            return -10**18
        opp_d = king(x, y, ox, oy)
        self_d = king(x, y, sx, sy)
        # Prefer states that reduce our distance more than theirs; encourage moving toward resources.
        best_r = -10**18
        for r in resources:
            try:
                tx, ty = parse_xy(r)
            except Exception:
                continue
            r_self = king(x, y, tx, ty)
            r_opp = king(ox, oy, tx, ty)
            # If both chase same target, advantage = opp_dist_to_target - my_dist_to_target (bigger is better)
            adv = r_opp - r_self
            if adv > best_r:
                best_r = adv
        if not resources:
            cx, cy = w // 2, h // 2
            best_r = -(king(x, y, cx, cy))
        # Secondary: avoid getting too close to opponent if no immediate resource advantage
        return best_r * 1000 + (opp_d - self_d) - self_d

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        sc = cell_score(nx, ny)
        if sc > best[0]:
            best = (sc, dx, dy)
    return [int(best[1]), int(best[2])]