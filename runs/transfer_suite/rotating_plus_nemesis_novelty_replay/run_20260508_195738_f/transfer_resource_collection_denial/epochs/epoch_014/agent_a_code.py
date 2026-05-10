def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = w - 1, h - 1
        if ox > sx:
            tx = 0
        if oy > sy:
            ty = 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for ddx, ddy in moves:
            nx, ny = sx + ddx, sy + ddy
            if valid(nx, ny):
                return [ddx, ddy]
        return [0, 0]

    res = [(int(x), int(y)) for x, y in resources]
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # After moving, evaluate best resource we could claim earlier than opponent
        score = 0
        best_diff = -10**18
        best_self = 10**18
        for rx, ry in res:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            diff = do - ds  # positive means we are closer
            # Prefer immediate contention, and also prefer smaller distance once tied
            if diff > best_diff or (diff == best_diff and ds < best_self):
                best_diff = diff
                best_self = ds
        # Primary: win contention; Secondary: reach sooner; Tertiary: avoid giving opponent a closer win next
        # If we can't beat opponent on any resource, bias toward resources that are far from opponent (increase their do-s gap negatively).
        score = best_diff * 100 - best_self
        # Small safety: discourage stepping closer to an opponent "hotspot" (closest resource to opponent) when not winning
        if best_diff <= 0:
            opp_target = min(res, key=lambda p: man(ox, oy, p[0], p[1]))
            score -= man(nx, ny, opp_target[0], opp_target[1]) * 2
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best