def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_adj_pen(x, y):
        p = 0
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            if (x + dx, y + dy) in obs:
                p += 1
        return p

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = None
    best_move = [0, 0]

    # If no resources are visible, drift toward opponent side while avoiding obstacles.
    if not resources:
        prefs = [(0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1)]
        tx = 1 if ox > sx else -1 if ox < sx else 0
        ty = 1 if oy > sy else -1 if oy < sy else 0
        for mx, my in prefs:
            nx, ny = sx + mx, sy + my
            if blocked(nx, ny):
                continue
            # Prefer moving toward opponent while keeping away from obstacles.
            score = -king_dist(nx, ny, ox, oy) - 0.5 * obs_adj_pen(nx, ny)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [mx, my]
        return best_move

    # Evaluate moves by (1) closeness to resources, (2) winning race vs opponent, (3) obstacle safety.
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if blocked(nx, ny):
            continue

        # Main objective: for the best resource "race", minimize (our_dist - opp_dist).
        best_race = None
        best_our = None
        for rx, ry in resources:
            d_our = king_dist(nx, ny, rx, ry)
            d_opp = king_dist(ox, oy, rx, ry)
            race = d_our - d_opp
            if best_race is None or race < best_race:
                best_race = race
            if best_our is None or d_our < best_our:
                best_our = d_our

        # Secondary: avoid moving into cramped obstacle-adjacent squares.
        # Tertiary tie-breaker: prefer moving slightly toward opponent (often opens lanes).
        score = (-10.0 * best_race) + (-1.0 * best_our) + (-0.4 * obs_adj_pen(nx, ny)) + (0.02 * king_dist(nx, ny, ox, oy))
        if best_score is None or score > best_score or (score == best_score and (mx, my) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [mx, my]

    # If all candidate moves blocked, stay.
    return best_move if best_move != [0, 0] or not any(not blocked(sx + mx, sy + my) for mx, my in moves) else [0, 0]