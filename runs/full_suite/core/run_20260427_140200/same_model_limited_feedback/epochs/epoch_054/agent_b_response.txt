def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy  # Chebyshev for 8-dir

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_score = -10**18

    # Simple deterministic mode switch: prefer nearer resources when behind, farther when ahead
    scores = observation.get("scores", {})
    my_score = scores.get(observation.get("self_name",""), None)
    opp_score = scores.get(observation.get("opponent_name",""), None)
    behind = False
    if isinstance(my_score, (int, float)) and isinstance(opp_score, (int, float)):
        behind = my_score < opp_score

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate advantage by targeting resources where we are significantly closer than opponent
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = dist((nx, ny), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            # If behind, be aggressive: maximize (opd - myd). If not, play safer: still maintain advantage but slightly penalize delay.
            gain = (opd - myd)
            speed = -myd
            # Mild "commitment": prefer resources closer to opponent's likely path by rewarding moderate gain and penalizing extreme isolation
            score = gain * 10 + speed * (2 if behind else 1)
            if score > local_best:
                local_best = score

        if local_best < -10**17:
            # No resources? move toward center as neutral
            local_best = -dist((nx, ny), (w//2, h//2))

        # Obstacle/space awareness: avoid moving into tight local corridors (count free neighbors)
        free_neighbors = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                free_neighbors += 1
        local_best += free_neighbors * 0.01

        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]