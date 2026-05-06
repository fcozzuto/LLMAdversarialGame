def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Focus: race resources where we can arrive earlier; otherwise, move to reduce opponent's best advantage.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Self's strongest winning option (min gap)
        best_win_gap = None
        best_win_dist = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            gap = sd - od  # negative => we arrive earlier
            if best_win_gap is None or gap < best_win_gap or (gap == best_win_gap and sd < best_win_dist):
                best_win_gap = gap
                best_win_dist = sd

        # If we can't win immediately, block: reduce opponent's nearest reachable resource distance advantage.
        opp_best_adv = None
        for rx, ry in resources:
            od = man(nx, ny, rx, ry)  # our position affects "interception" by denying ourselves? approximate
            oo = man(ox, oy, rx, ry)
            adv = oo - od  # opponent advantage if choosing that resource
            if opp_best_adv is None or adv < opp_best_adv:
                opp_best_adv = adv

        # Tie-break deterministically toward moving toward center to avoid oscillations.
        center = (w - 1) / 2.0, (h - 1) / 2.0
        center_score = (nx - center[0]) * (nx - center[0]) + (ny - center[1]) * (ny - center[1])

        # Rank:
        # 1) Prefer negative gap (we can beat opponent), minimize gap then our dist.
        # 2) If not, minimize opponent advantage (opp_best_adv), then our dist.
        if best_win_gap is not None and best_win_gap < 0:
            key = (0, best_win_gap, best_win_dist, center_score, dx, dy)
        else:
            key = (1, opp_best_adv if opp_best_adv is not None else 999, best_win_dist if best_win_dist is not None else 999, center_score, dx, dy)

        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]