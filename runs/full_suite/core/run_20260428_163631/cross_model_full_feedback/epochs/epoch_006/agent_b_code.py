def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(r) for r in observation.get("resources", [])]

    deltas = [(-1,-1), (0,-1), (1,-1),
              (-1, 0), (0,0), (1,0),
              (-1,1), (0,1), (1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # If stuck by obstacles, try to move to any valid cell
    valid_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid_moves.append((dx, dy))
    if not valid_moves:
        return [0, 0]

    # Heuristic: move toward closest resource that is favorable vs opponent,
    # break ties by closer to center to be deterministic.
    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    best_move = (0, 0)
    best_score = None

    target_resources = resources if resources else []
    center = (w//2, h//2)

    # Evaluate each possible move by resulting position
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        # score: prefer being closer to a resource while distant from opponent
        score = 0
        if target_resources:
            # choose nearest resource for this candidate
            d_me = min((man((nx, ny), r) for r in target_resources), default=0)
            d_opp = min((man((ox, oy), r) for r in target_resources), default=0)
            score += max(0, d_opp - d_me) * 2  # reward when we gain on resource
        # also prefer closer to center to stabilize determinism
        score += max(0, (man((nx, ny), center)))
        # also penalize getting too close to opponent
        score -= man((nx, ny), (ox, oy))

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves yield same score, stay if blocked from resources
    if best_score is None:
        best_move = (0, 0)

    return [best_move[0], best_move[1]]