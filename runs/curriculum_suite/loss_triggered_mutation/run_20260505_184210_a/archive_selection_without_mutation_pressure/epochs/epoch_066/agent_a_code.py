def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in moves if inside(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    def dist_manh(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def dist_chel(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    opp_edge = min(ox, w - 1 - ox, oy, h - 1 - oy)
    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
    center_focus = 1 if opp_edge <= 1 else 0  # opponent patrolling edges: punish hugging edges

    # Opponent baseline (use current opp position)
    if resources:
        opp_best = min(dist_manh(ox, oy, rx, ry) for rx, ry in resources)
    else:
        opp_best = 0

    best_dx, best_dy = legal[0]
    best_key = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if resources:
            my_best = min(dist_manh(nx, ny, rx, ry) for rx, ry in resources)
            # Want to be closer than opponent next to resource:
            # minimize (my_best - opp_best), also prefer smaller my_best.
            diff = my_best - opp_best
            # Secondary: maximize likelihood we "cut" edges by reducing Chebyshev distance to center if opponent is edge-close.
            cen = dist_chel(nx, ny, center_x, center_y)
            # Tertiary: discourage moving away from any resource
            my_near_2 = min(dist_chel(nx, ny, rx, ry) for rx, ry in resources)
            key = (diff, my_best, my_near_2, cen if center_focus else 0, dx, dy)
        else:
            # No resources: go center aggressively if opponent on edge
            cen2 = dist_chel(nx, ny, center_x, center_y)
            key = (cen2 if center_focus else 0, dx, dy)

        if best_key is None or key < best_key:
            best_key = key
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]