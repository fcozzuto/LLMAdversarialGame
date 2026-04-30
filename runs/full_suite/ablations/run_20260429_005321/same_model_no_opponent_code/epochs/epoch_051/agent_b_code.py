def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not resources:
        return [0, 0]

    candidates = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    deltas = []
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        deltas.append((dx, dy))

    if not deltas:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose resources we are "more likely" to take: self closer than opponent
    # If none, fallback to nearest resource.
    closer = []
    for r in resources:
        d_self = man((sx, sy), r)
        d_opp = man((ox, oy), r)
        if d_self <= d_opp:
            closer.append((d_self, r))
    if closer:
        closer.sort(key=lambda t: (t[0], t[1][0], t[1][1]))
        targets = [closer[i][1] for i in range(min(4, len(closer)))]
    else:
        resources_sorted = sorted(resources, key=lambda r: (man((sx, sy), r), r[0], r[1]))
        targets = resources_sorted[:4]

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy

        # Base: reduce distance to closest target(s)
        score = 0
        self_best = 10**9
        for t in targets:
            d = man((nx, ny), t)
            self_best = min(self_best, d)
        score -= self_best * 10

        # If we move onto a resource now, huge reward
        if [nx, ny] in resources:
            score += 10**6

        # Mild preference: stay away from squares that increase opponent's ability to immediately grab
        opp_best = 10**9
        for t in targets:
            d = man((ox, oy), t)
            opp_best = min(opp_best, d)
        # If our move gets too close to opponent while they are also near a target, penalize
        opp_dist_after = abs((ox - nx)) + abs((oy - ny))
        score -= max(0, (10 - opp_dist_after)) * 5

        # Tie-break: move that aligns toward the strongest target (lexicographic deterministic)
        # Choose one representative target deterministically.
        rep = min(targets, key=lambda r: (man((sx, sy), r), r[0], r[1]))
        dir_to_rep = (0 if rep[0] == nx else (1 if rep[0] > nx else -1),
                      0 if rep[1] == ny else (1 if rep[1] > ny else -1))
        score += (dx == dir_to_rep[0] and dy == dir_to_rep[1]) * 3

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move