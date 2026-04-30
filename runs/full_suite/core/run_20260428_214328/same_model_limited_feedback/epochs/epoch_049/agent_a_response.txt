def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    opp_dists = {}
    for rx, ry in resources:
        opp_dists[(rx, ry)] = max(abs(rx - ox), abs(ry - oy))

    def inb(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh

    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_opp_best = None
        for rx, ry in resources:
            myd = max(abs(rx - nx), abs(ry - ny))
            od = opp_dists[(rx, ry)]
            # Prefer being closer than opponent on a resource
            score = myd - 0.75 * od
            if my_opp_best is None or score < my_opp_best:
                my_opp_best = score
        # Also bias away from opponent to avoid easy grabs
        opp_dist = max(abs(nx - ox), abs(ny - oy))
        key = (my_opp_best, -opp_dist, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]