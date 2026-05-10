def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    # Target sets
    we_lead = int(observation.get("self_territory_count") or 0) >= int(observation.get("opponent_territory_count") or 0)
    if unclaimed:
        frontier = unclaimed
    else:
        # If nothing unclaimed, fall back to contesting opponent territory
        frontier = list(op_terr) if op_terr else [(sx, sy)]

    # Precompute distances to nearest frontier cell (approx)
    def nearest_dist(x, y, cells):
        best = 10**9
        if not cells: return best
        cap = 48 if len(cells) > 48 else len(cells)
        for i in range(cap):
            cx, cy = cells[i]
            d = abs(cx - x) + abs(cy - y)
            if d < best:
                best = d
                if best == 0: break
        return best

    # Bias toward cutting opponent if behind, else toward expansion
    op_target = list(op_terr) if op_terr else [(sx, sy)]
    dist_frontier_now = nearest_dist(sx, sy, frontier)
    dist_op_now = nearest_dist(sx, sy, op_target)

    best_move = [0, 0]
    best_score = -10**18

    ax, ay = sx, sy
    # Evaluate each neighbor move deterministically
    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = ax, ay  # invalid move: would be kept in place
            dx, dy = 0, 0
        cell = (nx, ny)

        # Heuristic components
        is_unclaimed = cell in set(unclaimed[:]) if unclaimed else False
        is_self = cell in self_terr
        is_opp = cell in op_terr

        df = nearest_dist(nx, ny, frontier)
        do = nearest_dist(nx, ny, op_target)

        # Improvement signals
        gain_frontier = (dist_frontier_now - df)
        gain_op = (dist_op_now - do)

        # Territory contest / expansion shaping
        score = 0
        if is_unclaimed:
            score += 3.0
        if is_opp:
            score += 5.0 if we_lead else 6.0
        if is_self:
            score += 0.2
        score += 1.2 * gain_frontier
        score += (0.9 if not we_lead else 0.3) * gain_op

        # Mild preference to not stall unless already strong
        if dx == 0 and dy == 0:
            score -= 0.4 if we_lead else 0.2

        # Deterministic tie-break: fixed move order (dirs order) by only updating on strictly better
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move