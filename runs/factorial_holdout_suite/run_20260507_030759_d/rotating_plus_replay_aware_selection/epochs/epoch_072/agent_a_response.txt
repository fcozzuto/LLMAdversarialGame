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

    if not resources or w <= 0 or h <= 0:
        return [0, 0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        return max(abs(c - a), abs(d - b))

    opp_best_move = None
    # Score a move by whether we can beat opponent on some resource; if not, minimize their lead and move toward best denial target.
    best_move = [0, 0]
    best_score = -10**18

    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        best_for_move = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            st = dist(nsx, nsy, rx, ry)
            ot = dist(ox, oy, rx, ry)
            lead = ot - st  # positive means we arrive earlier
            # Primary: biggest positive lead; Secondary: prefer shorter time; Tertiary: favor central-ish (rx+ry) small tie-break
            if lead >= 0:
                val = 10**7 + lead * 10**5 - st * 50 - (rx + ry) * 0.01
            else:
                # If we can't win it, denial: minimize opponent advantage (i.e., make lead closer to 0), and don't waste time.
                val = 10**6 - (-lead) * 10**5 - st * 5 + (rx + ry) * 0.001
            if val > best_for_move:
                best_for_move = val

        if best_for_move > best_score:
            best_score = best_for_move
            best_move = [mdx, mdy]

    if not isinstance(best_move, list):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]