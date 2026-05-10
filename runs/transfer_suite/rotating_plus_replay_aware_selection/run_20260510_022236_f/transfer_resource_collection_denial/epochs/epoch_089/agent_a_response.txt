def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    tr = int(observation.get("turns_remaining", 0))

    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid_res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            valid_res.append((x, y))
    if not valid_res:
        return [0, 0]

    def best_target_from(px, py):
        best = None
        for rx, ry in valid_res:
            ds = cheb_dist(px, py, rx, ry)
            do = cheb_dist(ox, oy, rx, ry)
            # Prefer winning races (ds<=do), otherwise minimize opponent advantage loss.
            if ds <= do:
                key = (0, ds, -do, rx, ry)
            else:
                key = (1, ds - do, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry), ds, do)
        return best[1], best[2], best[3]

    # Evaluate each move by how much it improves our racing position to the best target.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
        (tx, ty), ds, do = best_target_from(nx, ny)
        # Higher is better: negative ds, strong penalty if opponent is clearly closer.
        win_margin = do - ds
        time_bonus = 0 if tr <= 0 else (1 if ds <= tr else -1)
        on_resource = 1 if (nx, ny) == (tx, ty) else 0
        score = (2 * on_resource) + (5 * win_margin) - ds + time_bonus
        # Tie-break deterministically: prefer smaller dx then dy then lexicographic position.
        tiebreak = (-(win_margin >= 0), -on_resource, ds, do, dx, dy, nx, ny)
        if best_score is None or (score, -tiebreak[0], tiebreak[1], tiebreak[2], tiebreak[3], tiebreak[4], tiebreak[5], tiebreak[6], tiebreak[7]) > best_score:
            best_score = (score, -tiebreak[0], tiebreak[1], tiebreak[2], tiebreak[3], tiebreak[4], tiebreak[5], tiebreak[6], tiebreak[7])
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]