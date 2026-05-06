def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles_list = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**18

    if not resources:
        return [0, 0]

    # Precompute resource order for deterministic tie-breaks
    resources_sorted = sorted((r[0], r[1]) for r in resources)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # Local objective: maximize our distance-advantage to the best reachable resource
        local_best = -10**18
        local_res = None
        for rx, ry in resources_sorted:
            d_opp = cheb(ox, oy, rx, ry)
            d_self = cheb(nx, ny, rx, ry)
            adv = d_opp - d_self
            # Prefer stepping onto a resource very strongly, then better advantage, then closer distance, then lexicographic
            if (nx, ny) == (rx, ry):
                score = 10**9 + adv
            else:
                score = 1000 * adv - d_self
            if score > local_best:
                local_best = score
                local_res = (rx, ry)
            elif score == local_best and local_res is not None:
                if (d_self < cheb(nx, ny, local_res[0], local_res[1])) or (
                    d_self == cheb(nx, ny, local_res[0], local_res[1]) and (rx, ry) < local_res
                ):
                    local_res = (rx, ry)

        # Small preference to keep distance from opponent unless it helps advantage
        dist_keep = cheb(nx, ny, ox, oy)
        val = local_best + 0.01 * dist_keep

        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)
        elif val == best_val and best is not None:
            # Deterministic tie-break: lexicographically smallest move
            if (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]