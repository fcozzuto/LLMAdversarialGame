def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obs = observation.get("obstacles", [])
    blocked = set()
    for p in obs:
        if p is None:
            continue
        blocked.add((p[0], p[1]))
    if not resources:
        return [0, 0]

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Pick resource that favors us over opponent
    best_r = resources[0]
    best_val = None
    for rx, ry in resources:
        self_d = d2(sx, sy, rx, ry)
        opp_d = d2(ox, oy, rx, ry)
        val = opp_d - self_d
        if best_val is None or val > best_val or (val == best_val and self_d < d2(sx, sy, best_r[0], best_r[1])):
            best_val = val
            best_r = (rx, ry)
    tx, ty = best_r

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_s = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in blocked:
            nx, ny = sx, sy
        self_d = d2(nx, ny, tx, ty)
        opp_d = d2(nx, ny, ox, oy)
        # Prefer approaching target, discourage getting close to opponent, avoid unnecessary stalling
        score = -self_d * 2 + opp_d - (1 if (dx == 0 and dy == 0) else 0) * 3
        if best_s is None or score > best_s or (score == best_s and (nx, ny) != (sx, sy)):
            best_s = score
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]