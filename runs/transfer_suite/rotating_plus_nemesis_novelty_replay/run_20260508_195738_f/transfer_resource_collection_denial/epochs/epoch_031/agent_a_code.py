def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]
    res_set = set(resources)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mdist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        # Go for corner that is farther from opponent to reduce contention
        tx, ty = max(corners, key=lambda c: (mdist(ox, oy, c[0], c[1]) - 0.01 * mdist(sx, sy, c[0], c[1])))
        return [0 if tx == sx else (1 if tx > sx else -1), 0 if ty == sy else (1 if ty > sy else -1)]

    # Pick the resource with best "race" advantage
    best_r = None
    best_score = None
    for rx, ry in resources:
        ds = mdist(sx, sy, rx, ry)
        do = mdist(ox, oy, rx, ry)
        # If we're closer, heavily prefer; if tied, prefer lower self distance
        score = (do - ds) * 10 - ds
        if best_score is None or score > best_score:
            best_score = score
            best_r = (rx, ry)

    rx, ry = best_r

    # Evaluate one-step move: prioritize immediate collection, then improving race
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        immediate = 1 if (nx, ny) in res_set else 0
        ds_next = mdist(nx, ny, rx, ry)
        do_next = mdist(ox, oy, rx, ry)

        # Also nudge toward any nearby resources to reduce path brittleness
        nearest = min((mdist(nx, ny, arx, ary) for (arx, ary) in resources), default=0)
        # Keep from being predictable: if opponent is closer to our target, move to the next-closest alternative
        race_gap = do_next - ds_next
        val = immediate * 1000 + race_gap * 12 - ds_next * 2 - nearest * 0.3

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]