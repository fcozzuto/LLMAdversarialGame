def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Prefer immediate pickups, then deterministic "race" to best-deny target.
    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        my_pos = (nx, ny)
        pickup_bonus = 0
        if my_pos in set(res):
            pickup_bonus = 10**6  # must dominate

        # Score: smaller is better.
        # Race term favors resources where we are closer than opponent (or can overtake).
        # Deny term favors resources where opponent is currently closer.
        # Tie-break by deterministic secondary terms (y then x).
        my_best = 10**9
        opp_best = 10**9
        for r in res:
            md = cheb(my_pos, r)
            od = cheb((ox, oy), r)
            # race: (md-od) negative good; add to score scaled
            race = md - od
            # deny: prioritize if opponent is closer now (od<md) but we can still reach reasonably soon
            deny = 0
            if od < cheb((sx, sy), r):  # opponent already closer to r than we are
                deny = (md - od)  # less is better
            val = md + 0.35 * deny + 0.5 * race
            # secondary deterministic ordering
            val += 1e-6 * (r[1] * 8 + r[0])
            if val < my_best:
                my_best = val
            if od < opp_best:
                opp_best = od

        score = my_best + opp_best * 0.01 - pickup_bonus
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move