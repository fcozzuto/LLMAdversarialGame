def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    px, py = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def legal(nx, ny): return inb(nx, ny) and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            legal_moves.append((dx, dy, nx, ny))
    if not legal_moves:
        return [0, 0]

    def obs_pen(x, y):
        if not obstacles:
            return 0
        best = 99
        for ox, oy in obstacles:
            d = cheb(x, y, ox, oy)
            if d < best: best = d
        # Strongly discourage stepping next to obstacles, but still allow if needed
        if best <= 0: return 10**6
        if best == 1: return 18
        if best == 2: return 6
        return 0

    # Choose best move by assuming opponent also contests resources;
    # gain = how much closer we are to a resource compared to opponent.
    # If we're behind on all resources, switch to the most "deny" move (steer to least-inviting resources).
    opp_best = -10**9
    for rx, ry in resources:
        v = -cheb(px, py, rx, ry)
        if v > opp_best: opp_best = v
    # opp_best is negative distance; higher means better (closer). Normalize.
    opp_best_dist = 99
    if resources:
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if d < opp_best_dist: opp_best_dist = d

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy, nx, ny in legal_moves:
        score = -obs_pen(nx, ny)

        if resources:
            # maximize (opp_dist - our_dist) for a chosen target
            best_gain = -10**9
            best_denom = 10**9
            deny = 0
            for rx, ry in resources:
                our_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(px, py, rx, ry)
                gain = opp_d - our_d
                # tie-break toward nearer target to finish quickly
                if gain > best_gain or (gain == best_gain and our_d < best_denom):
                    best_gain = gain
                    best_denom = our_d

                # "deny": if opponent is very close, try to move toward resources that are far from them
                if opp_d <= 2:
                    deny = max(deny, our_d - opp_d)  # larger means we are farther than them

            # If we are generally behind, prioritize deny over gain
            behind = 1 if opp_best_dist < 3 else 0
            if behind:
                score += 2.5 * deny + 0.2 * best_gain
            else:
                score += 1.8 * best_gain

            # Small bonus for moving toward the overall nearest resource
            nearest = 99
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < nearest: nearest = d
            score += 0.05 * (10 - nearest)  # bounded-ish

        if