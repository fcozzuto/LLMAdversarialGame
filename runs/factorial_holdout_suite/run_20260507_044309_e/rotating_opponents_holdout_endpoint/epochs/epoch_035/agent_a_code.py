def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources_raw = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []

    resources = []
    for p in resources_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    # Aim: move to maximize "we-beat-opponent" slack from the next cell
    moves = [(0, 0), (1, 1), (1, 0), (0, 1), (1, -1), (-1, 1), (-1, 0), (0, -1), (-1, -1)]
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        best_slack = None
        best_selfd = None
        best_tx = None
        best_ty = None

        for tx, ty in resources:
            self_d = md(nx, ny, tx, ty)
            opp_d = md(ox, oy, tx, ty)
            slack = opp_d - self_d  # positive means we are closer
            if best_slack is None or (slack > best_slack) or (slack == best_slack and (self_d < best_selfd)) or (slack == best_slack and self_d == best_selfd and (tx < best_tx or (tx == best_tx and ty < best_ty))):
                best_slack = slack
                best_selfd = self_d
                best_tx, best_ty = tx, ty

        cand = (best_slack, -best_selfd, -best_tx, -best_ty, dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [best[4], best[5]]