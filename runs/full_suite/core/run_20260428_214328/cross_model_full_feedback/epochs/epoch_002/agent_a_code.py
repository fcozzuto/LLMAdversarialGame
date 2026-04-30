def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    occ = obstacles | {(ox, oy)}
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    best_score = -10**18
    best_move = (0, 0)

    if resources:
        # deterministically pick target: nearest, tie by coords
        best_res = None
        best_rd = 10**18
        for r in resources:
            rx, ry = r
            if (rx, ry) in obstacles:
                continue
            rd = man((sx, sy), (rx, ry))
            if rd < best_rd or (rd == best_rd and (rx, ry) < (best_res[0], best_res[1]) if best_res else True):
                best_rd = rd
                best_res = (rx, ry)
        if best_res is None:
            best_res = resources[0]
        tx, ty = best_res

        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            if (nx, ny) == (ox, oy):
                continue
            # primary: reduce distance to target; reward stepping onto a resource
            d_now = man((sx, sy), (tx, ty))
            d_new = man((nx, ny), (tx, ty))
            onto = 1 if (nx, ny) in set(tuple(p) for p in resources) else 0
            # secondary: keep away from opponent unless it helps grab target
            opp_d = man((nx, ny), (ox, oy))
            # tertiary: avoid moving into cells that are strictly worse wrt both axes (helps stability)
            axis_pen = -1 if (dx == 0 and dy == 0) else 0
            score = (d_now - d_new) * 1000 + onto * 500 + opp_d * 3 + axis_pen
            # subtle anti-capture: if opponent can also reach the target in fewer steps, prefer distancing
            if resources:
                opp_to_res = man((ox, oy), (tx, ty))
                self_to_res = d_new
                if self_to_res > opp_to_res:
                    score -= (self_to_res - opp_to_res) * 10
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
    else:
        # No resources: move to maximize distance if possible, else drift to a corner away from opponent
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            if (nx, ny) == (ox, oy):
                continue
            opp_d = man((nx, ny), (ox, oy))
            # deterministically prefer moving toward the farthest corner from opponent
            corners = [(0, 0), (0, h-1), (w-1, 0), (w-1, h-1)]
            far_corner = max(corners, key=lambda c: (man((c[0], c[1]), (ox, oy)), -(c[0]+c[1])))
            tcx, tcy = far_corner
            tc_dist = man((nx, ny), (tcx, tcy))
            score = opp_d * 1000 - tc_dist * 2
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]