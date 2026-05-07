def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if w <= 0 or h <= 0 or not resources:
        return [0, 0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def dist(a, b, c, d):
        return max(abs(c - a), abs(d - b))

    best = (None, -10**18)
    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        best_for_move = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            st = dist(sx + mdx, sy + mdy, rx, ry)
            ot = dist(ox, oy, rx, ry)
            # Primary: arrive earlier; secondary: biggest time advantage; tertiary: smaller own time.
            if st <= ot:
                adv = ot - st
                score = 10**6 + adv * 10**4 - st * 10 + (rx + ry) * 0.01
            else:
                # If we can't win it, still choose moves that reduce our loss and increase opponent delay.
                score = (st - ot) * -10**3 - st * 5 + (ot * 0.1)
            if score > best_for_move:
                best_for_move = score

        # If no reachable move improves, still pick the move that minimizes our distance to nearest resource.
        if best_for_move < -10**17:
            nearest = min(dist(nsx, nsy, rx, ry) for rx, ry in resources if (rx, ry) not in obstacles)
            best_for_move = -nearest

        if best_for_move > best[1]:
            best = ((mdx, mdy), best_for_move)

    return [int(best[0][0]), int(best[0][1])]