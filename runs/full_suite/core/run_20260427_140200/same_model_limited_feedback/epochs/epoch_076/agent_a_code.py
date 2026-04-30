def choose_move(observation):
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    self_name = observation.get("self_name", "agent_a")
    turn = observation.get("turn_index", 0)

    obs_set = set((x, y) for x, y in obstacles)
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_resource_value(mx, my):
        if not resources:
            return -10**9
        best = -10**9
        for rx, ry in resources:
            if (rx, ry) in obs_set:
                continue
            md = cheb(mx, my, rx, ry)
            od = cheb(ox, oy, rx, ry)
            val = (od - md) - 0.08 * md
            if val > best:
                best = val
        return best

    resource_mode = (turn % 2 == 0)
    best_dx, best_dy = 0, 0
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        opp_dist = cheb(nx, ny, ox, oy)
        res_val = best_resource_value(nx, ny)

        if resource_mode:
            score = res_val * 10 - 0.15 * opp_dist
        else:
            score = (-opp_dist) * 6 + res_val * 2

        # small deterministic tie-break: prefer moves with smaller dx^2+dy^2, then lexicographic
        if score > best_score or (score == best_score and (dx*dx + dy*dy) < (best_dx*best_dx + best_dy*best_dy)) or \
           (score == best_score and (dx*dx + dy*dy) == (best_dx*best_dx + best_dy*best_dy) and (dx, dy) < (best_dx, best_dy)):
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]