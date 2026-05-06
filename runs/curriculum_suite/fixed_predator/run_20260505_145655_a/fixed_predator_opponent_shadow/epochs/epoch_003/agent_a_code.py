def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) + abs(dy)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_val = -10**18

    opp_d0 = man(x, y, ox, oy)
    # If opponent is very close, shift to escape; otherwise, prioritize grabbing resources while keeping distance.
    escape_mode = opp_d0 <= 2
    chase_mode = (opp_d0 >= 4) and (len(resources) > 0)

    # Precompute nearest resource(s)
    target = None
    if resources:
        target = min(resources, key=lambda r: (man(x, y, r[0], r[1]), r[0], r[1]))

    # Deterministic tie-break ordering preference: stay > straight > diagonal (by dirs order).
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        opp_d = man(nx, ny, ox, oy)
        res_d = man(nx, ny, target[0], target[1]) if target else 0

        # Resource direction: encourage moving onto a resource cell.
        on_res = 1 if (target and nx == target[0] and ny == target[1]) else 0

        # Encourage not getting closer to opponent.
        delta_opp = opp_d - opp_d0

        # If opponent is close, strongly prefer increasing distance; else prefer decreasing resource distance.
        if escape_mode:
            val = 8.0 * delta_opp + 0.5 * on_res - 0.05 * res_d
        elif chase_mode:
            val = 2.5 * (-res_d) + 1.0 * delta_opp + 2.0 * on_res
        else:
            # Mixed: go for resources but keep safety margin.
            val = 2.0 * (-res_d) + 2.0 * max(-1, delta_opp) + 1.5 * on_res

        # Extra small deterministic preference: closer to nearest resource on ties is good; else more distance to opponent.
        val += 0.0001 * (opp_d - res_d)

        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]