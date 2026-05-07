def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cand = [(0, 0), (1, 1), (1, 0), (0, 1), (-1, 1), (1, -1), (-1, 0), (0, -1), (-1, -1)]
    best_move = (0, 0)
    best_val = -10**18

    # Competitive race: prefer resources where we can arrive no later than opponent.
    # Value = advantage - small movement cost to keep intent stable.
    opp_boost = 0.95
    my_cost_w = 0.08
    opp_cost_w = 0.06

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # evaluate next position against all visible resources, keep best.
        local_best = -10**18
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # If we're behind, penalize strongly; if tied/ahead, reward.
            adv = (op_d - my_d) * 1.0
            tie_bonus = 0.15 if my_d == op_d else 0.0
            val = adv + tie_bonus - my_cost_w * my_d - opp_cost_w * op_d
            if val > local_best:
                local_best = val

        # If multiple moves lead to similar resource race, move to increase distance from opponent a bit
        # when no clear advantage exists (prevents shadow blocking).
        if local_best < 0:
            dist_from_opp = cheb(nx, ny, ox, oy)
            local_best += 0.02 * dist_from_opp

        if local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]