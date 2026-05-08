def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def dist_cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resset = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resset.add((x, y))
    reslist = list(resset)

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not reslist:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_score = -10**9
    best_move = [0, 0]
    turns_left = int(observation.get("turns_remaining", 0))
    aggressive = (len(reslist) <= 4) or (turns_left <= 10)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if (nx, ny) in resset:
            base = 1000
        else:
            base = 0

        # Choose the target that maximizes our advantage after this move
        local_best = -10**9
        for tx, ty in reslist:
            d_our = dist_cheb(nx, ny, tx, ty)
            d_opp = dist_cheb(ox, oy, tx, ty)
            # Prefer resources we can reach not later than opponent; otherwise maximize advantage
            if aggressive:
                target_score = (d_opp - d_our) - 0.05 * d_our
            else:
                target_score = (d_opp - d_our) - 0.02 * d_our
                if d_opp < d_our:
                    target_score -= 3  # discourage letting opponent steal

            # Mild bias to near edges only when it doesn't hurt advantage
            edge_bias = (tx == 0 or tx == w - 1 or ty == 0 or ty == h - 1)
            if edge_bias:
                target_score += 0.1

            if target_score > local_best:
                local_best = target_score

        # Also prefer moves that increase distance from opponent when advantages are similar
        opp_dist = dist_cheb(nx, ny, ox, oy)
        final = base + local_best + (0.001 * opp_dist)

        # Deterministic tie-breaker: lexicographic on dx,dy ordering chosen above
        if final > best_score:
            best_score = final
            best_move = [dx, dy]

    return best_move