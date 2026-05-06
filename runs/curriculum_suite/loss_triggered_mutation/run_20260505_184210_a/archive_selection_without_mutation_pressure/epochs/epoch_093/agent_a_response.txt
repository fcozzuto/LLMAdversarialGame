def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if inside(nx, ny) else [0, 0]

    best_move = (0, 0)
    best_val = None  # lower is better
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue
        # If we can capture immediately, prefer it deterministically
        if (nx, ny) in set(resources):
            return [dx, dy]

        # Choose a target where we are relatively closer than the opponent
        worst_case = None
        for tx, ty in resources:
            myd = md(nx, ny, tx, ty)
            opd = md(ox, oy, tx, ty)
            rel = myd - opd  # negative = advantage
            # Prefer quicker conquest; penalize giving up too much advantage
            val = rel * 3 + myd
            if worst_case is None or val < worst_case:
                worst_case = val

        # Small tiebreak: keep distance from opponent to avoid being out-swept
        opp_push = md(nx, ny, ox, oy) * 0.02
        score = worst_case + opp_push

        if best_val is None or score < best_val:
            best_val = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]