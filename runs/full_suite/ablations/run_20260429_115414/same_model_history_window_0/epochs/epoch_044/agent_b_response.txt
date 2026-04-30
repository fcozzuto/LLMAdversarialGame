def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    if not resources:
        # Fallback: maximize distance from opponent while staying safe
        best = None
        best_score = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
                    nx, ny = sx, sy
                score = max(abs(nx - ox), abs(ny - oy))
                if best_score is None or score > best_score:
                    best_score = score
                    best = [dx, dy]
        return best if best is not None else [0, 0]

    def cheb(a, b, c, d):
        ax = a - c
        ay = b - d
        return ax if ax > ay else ay if ay > ax else ax

    best_move = [0, 0]
    best_score = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
                nx, ny = sx, sy
                dx, dy = 0, 0
            d_opp_now = cheb(ox, oy, nx, ny)

            # Choose resource that gives the biggest lead over opponent from this next position
            lead_best = None
            dist_best = None
            for rx, ry in resources:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                # Positive if we are closer (or can arrive at least as fast)
                lead = d_opp - d_self
                if lead_best is None or lead > lead_best:
                    lead_best = lead
                    dist_best = d_self
                elif lead == lead_best and d_self < dist_best:
                    dist_best = d_self

            # Strategy: prioritize taking/contesting resources where we have (or can gain) an advantage,
            # but keep some separation from opponent to reduce race losses.
            score = (lead_best * 3.0) - (dist_best * 0.6) - (d_opp_now * 0.25)

            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move