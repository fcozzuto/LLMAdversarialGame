def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = (0, 0)
        best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in occ:
                d = cheb(nx, ny, ox, oy)
                # small obstacle-avoid bias
                adj = 0
                for ax in (-1, 0, 1):
                    for ay in (-1, 0, 1):
                        if ax == 0 and ay == 0:
                            continue
                        if (nx + ax, ny + ay) in occ:
                            adj += 1
                key = (d + adj * 0.25, d, nx, ny)
                if best_key is None or key < best_key:
                    best_key = key
                    best = (dx, dy)
        return [best[0], best[1]]

    def hazard(x, y):
        # Penalize closeness to obstacles more strongly if it restricts movement.
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in occ:
                    # orthogonal adjacency hurts more
                    pen += 3 if (ax == 0 or ay == 0) else 2
        return pen

    # "Race" heuristic: pick moves that maximize lead to the best resource (opp distance - our distance).
    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        our_h = hazard(nx, ny)
        # If we are closer to opponent than them to us, slightly avoid running into their capture corridor.
        opp_threat = 0
        if cheb(nx, ny, ox, oy) < cheb(sx, sy, ox, oy):
            # encourage not to "over-approach" if it doesn't improve resource leads
            opp_threat = 0.75

        best_res = None
        for rx, ry in resources:
            d_our = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            lead = d_opp - d_our  # positive means we can arrive earlier than opponent
            # tie-break: prefer nearer resources and avoid obstacles near them
            res_h = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (rx + ax, ry + ay) in occ:
                        res_h += 1
            key = (-(lead * 10 - res_h * 0.6), d_our, rx, ry)  # minimal key for chosen resource
            if best_res is None or key < best_res:
                best_res = key

        # Convert chosen resource preference into a move key
        # Recompute lead from the chosen resource embedded in best_res
        # best_res is (primary, d_our, rx, ry)
        chosen_rx, chosen_ry = best_res[2], best_res[3]
        lead = cheb(ox, oy, chosen_rx, chosen_ry) - cheb(nx, ny, chosen_rx, chosen_ry)
        move_value = lead * 10 - our_h - opp_th