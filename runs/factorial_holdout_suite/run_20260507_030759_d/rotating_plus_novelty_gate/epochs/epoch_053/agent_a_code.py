def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]

    dxs = (-1, 0, 1)
    legal = []
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if (sx, sy) in set(resources):
        return [0, 0]
    if not resources:
        # move to maximize separation from opponent while staying safe
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            sep = abs(nx - ox) + abs(ny - oy)
            key = (-sep, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    res_set = set(resources)
    best_key = None
    best_move = (0, 0)

    # Prefer moves that let us be closer to a resource than the opponent,
    # with a small bonus for targeting near resources and avoiding "late races".
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # If we can collect immediately, take it deterministically.
        if (nx, ny) in res_set:
            best_move = (dx, dy)
            break

        best_for_cell = None
        for rx, ry in resources:
            self_d = manh(nx, ny, rx, ry)
            opp_d = manh(nx, ny, ox, oy)
            # advantage: positive means we are closer to this resource than opponent
            adv = opp_d - self_d
            # Encourage earlier collection; penalize being far.
            near_bonus = 2.0 / (1 + self_d)
            # Encourage moves where the opponent is also not "too close" to steal.
            steal_penalty = -0.35 * (1 / (1 + opp_d))
            val = adv + near_bonus + steal_penalty

            # tie-break: larger val, then smaller self_d, then smaller opp_d, then dx,dy
            cell_key = (-val, self_d, opp_d)
            if best_for_cell is None or cell_key < best_for_cell[0]:
                best_for_cell = (cell_key, val)

        cell_key = (best_for_cell[0], dx, dy)
        if best_key is None or cell_key < best_key:
            best_key = cell_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]