def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    best_score = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Score: how much closer we are to a resource than the opponent (and avoid giving them a big advantage).
        score = -10**9
        for r in resources:
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            d_our = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            s = (d_opp - d_our) * 100 - d_our
            if s > score:
                score = s

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]