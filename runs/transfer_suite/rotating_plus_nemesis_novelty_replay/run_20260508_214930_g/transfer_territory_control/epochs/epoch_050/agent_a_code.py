def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    resources = set(tuple(p) for p in (observation.get("resources") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best_mv = [0, 0]
    best_sc = -10**18
    my_dist = dist2(sx, sy, ox, oy)
    turn = observation.get("turn_index", 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sc = 0
        if (nx, ny) in resources:
            sc += 8
        if (nx, ny) in unclaimed:
            sc += 14
        if (nx, ny) in self_t:
            sc += 6
        if (nx, ny) in opp_t:
            sc -= 10
        # expansion preference: closer to unclaimed or to opponent (when beneficial)
        sc += -0.06 * dist2(nx, ny, ox, oy)
        if (turn % 6) == 0:
            sc += -0.04 * dist2(nx, ny, sx, sy)
        if dist2(nx, ny, ox, oy) < my_dist:
            sc += 1.5  # moving toward opponent
        if (nx, ny) == (ox, oy):
            sc += 20
        if sc > best_sc:
            best_sc = sc
            best_mv = [dx, dy]

    return best_mv