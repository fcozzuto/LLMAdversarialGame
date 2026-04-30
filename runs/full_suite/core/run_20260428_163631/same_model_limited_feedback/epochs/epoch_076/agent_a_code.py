def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    # Chebyshev distance matches king-like movement (8-dir)
    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    # Choose best resource: prioritize reachable proximity, but avoid targets opponent is closer to
    best = None
    best_key = None
    for r in resources:
        r = (r[0], r[1])
        if r in obstacles:
            continue
        d_self = dist((sx, sy), r)
        d_opp = dist((ox, oy), r)
        # If opponent is closer, penalize; otherwise reward
        closer_penalty = 0 if d_self <= d_opp else (d_self - d_opp) * 2 + 1
        # Tie-break by resource coordinates deterministically
        key = (closer_penalty, d_self, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best = r
    target = best if best is not None else (sx, sy)

    # Move one step toward target (8-direction), avoid obstacles
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer reducing distance to target; slight repulsion from opponent if too close
        d = dist((nx, ny), target)
        opp_d = dist((nx, ny), (ox, oy))
        danger = 0
        if opp_d <= 1:
            danger = 5 + (1 - opp_d) * 3
        # If staying on target is possible, that's best
        picked = 0 if (nx, ny) == target else 1
        score = (danger, d, picked, (nx - sx) * 2 + (ny - sy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]