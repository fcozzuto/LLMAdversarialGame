def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    def is_ev(r):
        r = (r or "").replace("-", "_")
        return ("evad" in r) or (r == "evader")
    def is_pu(r):
        r = (r or "").replace("-", "_")
        return ("purs" in r) or (r == "pursuer")

    pursuer = False
    if is_pu(self_role) and not is_ev(self_role):
        pursuer = True
    elif is_pu(opp_role) and not is_ev(opp_role):
        pursuer = False
    else:
        pursuer = True  # default

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_free(x, y):
        return inb(x, y) and (x, y) not in obs

    def d2(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx * dx + dy * dy

    best = (None, -10**18)
    for i, (dx, dy) in enumerate(deltas):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine would keep in place
        dist = d2(nx, ny, ox, oy)
        if pursuer:
            score = -dist  # minimize distance
        else:
            score = dist   # maximize distance

        # Secondary objective: steer towards/away from a corner depending on role
        target_corner = corners[(observation.get("turn_index", 0) + i) % 4]
        corner_dist = d2(nx, ny, target_corner[0], target_corner[1])
        if pursuer:
            score -= 0.05 * corner_dist  # stay mobile but don't waste time
        else:
            score += 0.05 * corner_dist  # pull to a corner

        # Mild preference for not staying still (unless forced)
        if dx == 0 and dy == 0 and (sx, sy) in obs:
            score -= 1
        if dx == 0 and dy == 0:
            score -= 0.02

        if score > best[1]:
            best = ((dx, dy), score)

    dx, dy = best[0]
    return [int(dx), int(dy)]