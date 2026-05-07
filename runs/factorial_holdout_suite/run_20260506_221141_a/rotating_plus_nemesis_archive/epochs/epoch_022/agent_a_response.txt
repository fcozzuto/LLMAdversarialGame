def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if not resources:
        return [0, 0]
    if (sx, sy) in obstacles:
        return [0, 0]
    if (sx, sy) in set(map(tuple, resources)):
        return [0, 0]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Decide whether to contest or race based on relative distances
    ahead_or_tied = []
    behind_all_best = None  # (key, resource)
    for rx, ry in resources:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        d = sd - od
        if d <= 0:
            ahead_or_tied.append((sd, rx, ry))
        else:
            # when behind everywhere, prefer resources opponent is far from, but still get close to one
            key = (-(od), sd, rx * 8 + ry)
            if behind_all_best is None or key > behind_all_best[0]:
                behind_all_best = (key, (rx, ry))

    if ahead_or_tied:
        # pick closest resource we can reach not later than opponent
        ahead_or_tied.sort()
        tx, ty = ahead_or_tied[0][1], ahead_or_tied[0][2]
    else:
        tx, ty = behind_all_best[1][0], behind_all_best[1][1]

    best_move = [0, 0]
    best_score = None
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_after = manh(nx, ny, tx, ty)
        opp_after = manh(ox, oy, tx, ty)
        # primary: reduce distance to chosen target
        # secondary: keep/increase advantage over opponent regarding the same target
        adv_after = opp_after - my_after
        # tertiary: mildly move away from opponent to reduce immediate contest pressure
        opp_dist_now = manh(nx, ny, ox, oy)
        score = (-(my_after), adv_after, -opp_dist_now, -(tx * 8 + ty))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move