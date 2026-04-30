def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    deltas = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    best = None
    best_move = (0, 0)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        target_list = resources
    else:
        target_list = [(w // 2, h // 2)]

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Primary: get closer to nearest resource
        nd = 10**9
        for r in target_list:
            d = dist((nx, ny), r)
            if d < nd:
                nd = d

        # Secondary: keep away from opponent (helps when competing resources)
        od = dist((nx, ny), (ox, oy))

        # Deterministic combined scoring (smaller is better for nd, larger for od)
        score = (nd, -od, abs(dx) + abs(dy))
        if best is None or score < best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]