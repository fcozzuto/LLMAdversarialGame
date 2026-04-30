def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Choose among the best few resources by current "capture advantage"
    if resources:
        best_resources = []
        for r in resources:
            d_me = cheb((sx, sy), r)
            d_op = cheb((ox, oy), r)
            # Prefer resources where we are closer or can get ahead.
            adv = (d_op - d_me) * 20 - d_me
            best_resources.append((adv, r))
        best_resources.sort(key=lambda t: (-t[0], t[1][0], t[1][1]))
        target_candidates = [r for _, r in best_resources[: min(4, len(best_resources))]]
    else:
        target_candidates = [(w - 1, h - 1), (0, 0), (w // 2, h // 2)]

    # Additional heuristic: "interference" point near opponent->resource line (roughly)
    def interference_score(x, y):
        # Encourage staying on/near the median Chebyshev path from opponent to target
        if not target_candidates:
            return 0
        best = -10**9
        for r in target_candidates:
            # Path should progress both axes; bias toward cells that reduce opponent gain
            d_op = cheb((ox, oy), r)
            d_op_now = cheb((x, y), r)
            # If we are closer to r than opponent, it's strong interference.
            s = (d_op - d_op_now) * 12 - d_op_now
            if s > best:
                best = s
        return best

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Main evaluation: expected advantage on candidate targets from the next position
        val = 0
        for r in target_candidates:
            d_me = cheb((nx, ny), r)
            d_op = cheb((ox, oy), r)
            # We want to be ahead; also avoid giving opponent a much better position.
            val += (d_op - d_me) * 25 - d_me

        # Interference term to change policy from simple greedy chasing
        val += interference_score(nx, ny) * 0.6

        # Discourage moves that step into "trap proximity" of opponent (reduce collisionless disadvantage)
        # (still deterministic, no randomness)
        d_opp_next = cheb((nx, ny), (ox, oy))
        val -= (4 - d_opp_next) * 6 if d_opp_next < 4 else 0

        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]