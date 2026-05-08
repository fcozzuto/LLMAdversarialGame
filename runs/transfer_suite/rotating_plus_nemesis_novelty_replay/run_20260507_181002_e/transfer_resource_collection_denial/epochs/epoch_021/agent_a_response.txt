def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            q = v.get("position", v.get("pos", None))
            if isinstance(q, (list, tuple)) and len(q) == 2:
                return int(q[0]), int(q[1])
        return None

    obs = set()
    for o in obstacles:
        t = to_xy(o)
        if t:
            x, y = t
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        t = to_xy(r)
        if t:
            x, y = t
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    if not res:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a target where we are currently closer than the opponent (priority), else least contested.
    best = None
    best_key = None
    for x, y in res:
        ds = man(sx, sy, x, y)
        do = man(ox, oy, x, y)
        lead = do - ds  # higher is better
        key = (lead, -do, ds, x, y)
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)
    tx, ty = best

    # Local move evaluation with obstacle avoidance and blocking.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            score = -10**9
        else:
            self_to = man(nx, ny, tx, ty)
            # If we can step onto/near contested resource, value more.
            opp_to = man(ox, oy, tx, ty)
            # Penalize moving away from the resource while reward progress.
            progress = best_key[0] + (opp_to - self_to)
            # Obstacle proximity penalty to avoid corners.
            near_obs = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    px, py = nx + ax, ny + ay
                    if (px, py) in obs:
                        near_obs += 1
            score = (progress * 1000) - self_to - (near_obs * 3) - (1 if dx == 0 and dy == 0 else 0)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]