def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -cheb(nx, ny, tx, ty)
            if best is None or v > best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # For each candidate move, pick best resource target for us and compute an advantage score.
    best_overall = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        best_target = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)

            # Prefer resources where we are closer, and also where we will deny opponent access.
            # Small tiebreakers to reduce oscillation: prefer moving generally toward center and away from staying.
            adv = (do - ds)
            center_bias = -cheb(nx, ny, w // 2, h // 2) * 0.01
            move_bias = -0.001 * (dx == 0 and dy == 0)
            # If we're very close, strongly commit.
            commit = 2.0 / (1 + ds)
            # If opponent is already much closer, deprioritize (resource denial).
            deny = -1.0 / (1 + max(0, ds - do + 1))
            score = adv + commit + deny + center_bias + move_bias

            if best_target is None or score > best_target[0]:
                best_target = (score, ds, do, rx, ry)

        if best_overall is None or best_target[0] > best_overall[0]:
            best_overall = (best_target[0], dx, dy)
    return [best_overall[1], best_overall[2]] if best_overall else [0, 0]