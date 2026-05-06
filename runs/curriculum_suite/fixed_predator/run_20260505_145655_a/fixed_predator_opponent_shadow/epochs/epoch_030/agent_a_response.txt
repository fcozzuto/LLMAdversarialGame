def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def clamp01(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        dx = sign(ox - x)
        dy = sign(oy - y)
        return [dx, dy]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            nx, ny = x, y  # engine will keep us in place

        s = 0
        for rx, ry in resources:
            me_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Prefer resources where we are (or become) closer than opponent.
            # Strongly discourage moves that let opponent keep a big advantage.
            lead = opp_d - me_d
            s += (lead * 50) - (me_d * 2) + (opp_d * 0.05)
            # Mild urgency: closer resources matter more when count is low.
            if len(resources) <= 6:
                s += 25 / (1 + me_d)
        # Secondary: reduce distance to opponent to increase contest pressure.
        s += (man(nx, ny, ox, oy) * -0.1)

        if s > best_score:
            best_score = s
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]