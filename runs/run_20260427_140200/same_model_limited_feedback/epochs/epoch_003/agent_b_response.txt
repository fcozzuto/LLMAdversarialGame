def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # drift toward opponent to potentially contest future resources
        best = (-(10**9), 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = dist(nx, ny, ox, oy)
            score = -d
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]
    # Evaluate contested advantage after making the move
    best_score = -(10**18)
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # If we land on a resource, prioritize strongly
        landing_bonus = 0
        if (nx, ny) in set(tuple(p) for p in resources):
            landing_bonus = 1000
        cur = 0
        for rx, ry in resources:
            ts = dist(nx, ny, rx, ry)
            to = dist(ox, oy, rx, ry)
            # Prefer resources we can reach strictly earlier, else prefer reducing our lead deficit.
            cur += (to - ts) * 10 - ts * 0.5
        # Additionally, encourage moving closer to the best immediate resource
        best_immediate = -(10**18)
        for rx, ry in resources:
            ts = dist(nx, ny, rx, ry)
            to = dist(ox, oy, rx, ry)
            score_r = (to - ts) * 20 - ts
            if score_r > best_immediate:
                best_immediate = score_r
        total = cur * 0.05 + best_immediate + landing_bonus
        # Tie-break deterministically by fixed move ordering
        if total > best_score:
            best_score = total
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]