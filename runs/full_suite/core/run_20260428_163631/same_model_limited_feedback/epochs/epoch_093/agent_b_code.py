def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    if not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Evaluate resources by contest advantage (prefer ones opponent is less able to reach first).
    best = None
    best_score = -10**9
    for r in resources:
        sd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        # Primary: make us arrive strictly earlier (positive). Secondary: arrive sooner.
        score = (od - sd) * 100 - sd
        if score > best_score:
            best_score = score
            best = r
        elif score == best_score and sd < dist((sx, sy), best):
            best = r

    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Choose move that reduces distance to target while avoiding obstacles and not moving into opponent if avoidable.
    best_move = (0, 0)
    best_mscore = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to = dist((nx, ny), (tx, ty))
        d_opp = dist((nx, ny), (ox, oy))
        # Penalize allowing opponent to get very close; prefer bigger separation.
        mscore = (-d_to) * 10 + (d_opp) * 2
        # Slightly discourage staying when movement can improve.
        if dx == 0 and dy == 0:
            mscore -= 1
        if mscore > best_mscore:
            best_mscore = mscore
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]