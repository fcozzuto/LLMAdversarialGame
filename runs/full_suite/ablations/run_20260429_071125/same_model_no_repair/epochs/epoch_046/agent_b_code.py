def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Evaluate each candidate move by the best resource "standing" for us vs opponent after the move.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        us_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            du = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach no later; heavily penalize if opponent can beat us.
            if du <= do:
                # Primary: advantage (opponent slower). Secondary: closer.
                val = 200 - 8 * du + 12 * (do - du)
            else:
                # Deny: maximize opponent's distance even if we won't get it.
                val = 80 - 6 * do - 4 * du
            # Small preference for resource count remaining: act when fewer left.
            rem = observation.get("remaining_resource_count", len(resources))
            if rem is not None:
                val += (12 - int(rem)) * 0.5
            # Tie-break deterministically by coordinates.
            val += -0.001 * (rx * 8 + ry)
            if val > us_best:
                us_best = val

        if us_best > best_score:
            best_score = us_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]