def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            nx, ny = sx, sy

        # If we could step onto a resource, strongly prefer it.
        step_res_bonus = 0
        for rx, ry in resources:
            if (nx, ny) == (rx, ry):
                step_res_bonus = 10**9
                break

        # Choose the most promising resource under this move.
        new_self = nx, ny
        best_resource_val = -10**18
        best_comp = None
        for rx, ry in resources:
            dS = md(new_self[0], new_self[1], rx, ry)
            dO = md(ox, oy, rx, ry)
            # Prioritize resources we can reach first; otherwise deny by increasing opponent lead.
            lead = dO - dS
            # Tie-break toward closer-to-it for us (more likely to keep advantage).
            val = lead * 1000 - dS
            if val > best_resource_val or (val == best_resource_val and (rx, ry) < best_comp):
                best_resource_val = val
                best_comp = (rx, ry)

        # Denial: keep distance from opponent unless we can collect immediately.
        opp_adj = md(nx, ny, ox, oy)
        block_pen = 0
        if opp_adj <= 1:
            block_pen = 2000 - opp_adj * 1000
        else:
            block_pen = 0

        # Small preference for moving toward center to reduce dead ends.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pref = -((nx - cx) ** 2 + (ny - cy) ** 2)

        total = step_res_bonus + best_resource_val - block_pen + center_pref
        if total > best_val or (total == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = total
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]