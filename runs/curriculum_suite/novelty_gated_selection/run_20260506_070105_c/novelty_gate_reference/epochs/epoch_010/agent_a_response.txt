def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = w // 2, h // 2

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((r[0], r[1]))

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If any move immediately reaches a resource, take it deterministically.
    resset = set(res)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in resset:
            return [dx, dy]

    best = [0, 0]
    best_score = -10**18

    # Strategy: for each move, choose the target resource where we beat opponent by distance,
    # otherwise fall back to center pressure while staying obstacle-safe.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        oppd = md(nx, ny, ox, oy)
        centd = md(nx, ny, cx, cy)

        if res:
            # Score by best advantage over opponent among resources, then distance.
            best_adv = -10**9
            best_dist = 10**9
            for rx, ry in res:
                selfd = md(nx, ny, rx, ry)
                opp_to_res = md(ox, oy, rx, ry)
                # advantage: how much closer we are now compared to what opponent would need
                adv = (opp_to_res - selfd)
                if adv > best_adv or (adv == best_adv and selfd < best_dist):
                    best_adv = adv
                    best_dist = selfd
            # Encourage contesting when we can be ahead (adv>0), otherwise drift to center.
            contest_term = best_adv * 1000
            reach_term = -best_dist
        else:
            contest_term = 0
            reach_term = -centd

        # Additional penalty: don't allow giving the opponent too much proximity.
        # We want to reduce opponent distance a bit while progressing.
        opp_term = -oppd * 0.5

        score = contest_term + reach_term + opp_term + (-(centd) * 0.15)
        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best