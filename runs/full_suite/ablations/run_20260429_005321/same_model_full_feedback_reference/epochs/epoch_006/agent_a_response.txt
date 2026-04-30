def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            res.append((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_for(x, y):
        if not res:
            # If no visible resources: drift toward center and keep some separation from opponent.
            center = (w // 2, h // 2)
            return -dist((x, y), center) + (dist((x, y), (ox, oy)) * 0.1)
        ds = min(dist((x, y), r) for r in res)
        do = min(dist((ox, oy), r) for r in res)
        return (100 - ds) - 0.6 * do  # prefer states closer to resources than opponent

    best_move = (0, 0)
    best_score = -10**18

    # Tie-break deterministically by fixed move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_min = 10**9
        opp_min = 10**9
        if res:
            my_min = min(dist((nx, ny), r) for r in res)
            opp_min = min(dist((ox, oy), r) for r in res)

        # Main objective: maximize advantage to nearest resource.
        adv = (opp_min - my_min)
        score = adv * 10.0

        # Secondary: prefer being closer overall; reward nearing at least one resource.
        score += (30.0 - my_min) if res else best_for(nx, ny)

        # Extra: mildly discourage stepping onto cells adjacent to obstacles (avoid traps).
        if obstacles:
            adj_pen = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    xx, yy = nx + ax, ny + ay
                    if (xx, yy) in obs:
                        adj_pen += 1
            score -= adj_pen * 0.8

        # If resources exist, also prefer moves that reduce distance to opponent when we are winning nearby
        # (helps deny in later turns).
        if res and adv > 0:
            score += dist((ox, oy), (nx, ny)) * 0.02

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]