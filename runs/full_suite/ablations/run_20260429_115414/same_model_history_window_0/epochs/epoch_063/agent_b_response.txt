def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp_move(nx, ny):
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            return (sx, sy)
        if (nx, ny) in obstacles:
            return (sx, sy)
        return (nx, ny)

    if not resources:
        # Fallback: drift toward opponent corner
        dx = -1 if sx > w - 1 - ox else 1 if sx < w - 1 - ox else 0
        dy = -1 if sy > h - 1 - oy else 1 if sy < h - 1 - oy else 0
        nx = sx + dx
        ny = sy + dy
        nx, ny = clamp_move(nx, ny)
        return [nx - sx, ny - sy]

    self_target = min(resources, key=lambda r: dist((sx, sy), r))
    opp_target = min(resources, key=lambda r: dist((ox, oy), r))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    for mdx, mdy in moves:
        nx, ny = clamp_move(sx + mdx, sy + mdy)
        # Main change vs prior: contest opponent's likely target rather than only nearest-to-self
        d_self = dist((nx, ny), self_target)
        d_opp = dist((nx, ny), opp_target)
        d_opp_from_target = dist((ox, oy), opp_target)
        # If we can get closer than opponent, prioritize; otherwise still move toward opp_target
        contest = 0
        if d_opp < d_opp_from_target:
            contest = 20 - 5 * d_opp
        # Also lightly prefer moving away from opponent to reduce their advantage (deterministic)
        d_opp_agent = dist((nx, ny), (ox, oy))
        score = (-2 * d_self) + (-1.5 * d_opp) + contest + (0.03 * d_opp_agent)

        if best_score is None or score > best_score or (score == best_score and (mdx, mdy) < best):
            best_score = score
            best = (mdx, mdy)

    return [best[0], best[1]]