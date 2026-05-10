def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Fallback: move to corner farthest from opponent to reduce interference.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        bestp, bestm = -10**9, [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            d = max(cheb(nx, ny, c[0], c[1]) for c in corners)
            opp = cheb(nx, ny, ox, oy)
            p = d - 0.2 * opp
            if p > bestp:
                bestp, bestm = p, [dx, dy]
        return bestm

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        win_count = 0
        margin_sum = 0
        block_sum = 0
        # Evaluate after-move race dynamics
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_me <= d_opp:
                win_count += 1
                margin_sum += (d_opp - d_me)
            else:
                # Penalize giving opponent a clear advantage on targets
                block_sum -= (d_me - d_opp)

        # Extra deterministic tie-break: prefer reducing distance to closest target we can contest
        closest_contest = 10**9
        for rx, ry in resources:
            if cheb(nx, ny, rx, ry) <= cheb(ox, oy, rx, ry):
                v = cheb(nx, ny, rx, ry)
                if v < closest_contest:
                    closest_contest = v
        if closest_contest == 10**9:
            closest_contest = min(cheb(nx, ny, rx, ry) for rx, ry in resources)

        # Composite score
        score = 1000 * win_count + 10 * margin_sum + 2 * block_sum - 0.1 * closest_contest

        # Second tie-break: closer to opponent's current position slightly to prevent them farming safely
        score += -0.02 * cheb(nx, ny, ox, oy)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move