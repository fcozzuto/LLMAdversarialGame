def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    closer = []
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        closer.append((od - sd, -sd, rx, ry, sd, od))

    best = None
    for item in closer:
        adv, neg_sd, rx, ry, sd, od = item
        if adv > 0:
            if best is None or (adv, sd) > (best[0], best[4]):
                best = item

    if best is None:
        # Opponent is closer to everything: contest the most urgent (smallest opponent distance)
        best = min(closer, key=lambda t: (t[5], t[4]))  # (od, sd)

    _, _, tx, ty, _, _ = best

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Try to move that minimizes distance to target with obstacle avoidance.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = dist(nx, ny, tx, ty)
        # Small penalty for moving away from target; prefer not to step-stay if ties
        score = (d_to_t, 1 if (dx == 0 and dy == 0) else 0)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]