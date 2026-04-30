def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_score = None

    # If no resources, drift toward center while keeping distance from opponent
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            score = dist((nx, ny), (cx, cy)) - 0.1 * dist((nx, ny), (ox, oy))
            if best_score is None or score < best_score:
                best_score, best_move = score, (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                continue

        self_d = 10**9
        opp_d = 10**9
        advantage = -10**9
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            if sd < self_d: self_d = sd
            if od < opp_d: opp_d = od
            adv = od - sd
            if adv > advantage: advantage = adv

        # Prefer moves that make us relatively closer to some resource than the opponent.
        # Add small tie-breaks: closer to resources, farther from opponent to avoid swaps, and stay safer.
        score = (-advantage, self_d, dist((nx, ny), (ox, oy)))
        if best_score is None or score < best_score:
            best_score, best_move = score, (dx, dy)

    return [best_move[0], best_move[1]]