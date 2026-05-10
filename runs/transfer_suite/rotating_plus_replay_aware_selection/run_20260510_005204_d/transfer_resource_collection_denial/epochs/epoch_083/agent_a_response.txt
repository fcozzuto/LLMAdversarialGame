def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp(x, a, b):
        return a if x < a else (b if x > b else x)

    def blocked(x, y):
        return (x, y) in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def best_target_value(px, py):
        # Maximize "how much closer we are than opponent" and then closeness.
        best = None
        for rx, ry in resources:
            myd = cheb(px, py, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Primary: (opd - myd) (prefer resources we can beat), Secondary: smaller myd, then deterministic coords.
            key = (opd - myd, -myd, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, rx, ry, myd, opd)
        key, rx, ry, myd, opd = best
        # Add a small bias to "secure" resources we're already at least as close to.
        sec = 5 if myd <= opd else 0
        return key, sec, rx, ry, myd, opd

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        if blocked(nx, ny):
            nx, ny = sx, sy  # engine would keep us in place
        (key, sec, rx, ry, myd, opd) = best_target_value(nx, ny)

        # If opponent is winning a target (opd < myd), prioritize reducing our distance to the best contested resource.
        # Otherwise prioritize actual lead (opd - myd) and reaching it quickly.
        lead = opd - myd
        contested_penalty = 0 if myd <= opd else (-lead)
        score = (lead, -myd, sec, -contested_penalty, -rx, -ry)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]