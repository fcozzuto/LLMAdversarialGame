def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = observation.get("resources") or []
    sr = (observation.get("self_role") or "").lower()
    orr = (observation.get("opponent_role") or "").lower()

    is_self_pursuer = ("purs" in sr) and ("evad" not in sr and "escape" not in sr and "runner" not in sr)
    is_opp_pursuer = ("purs" in orr) and ("evad" not in orr and "escape" not in orr and "runner" not in orr)
    self_pursuer = is_self_pursuer or (not is_opp_pursuer and "purs" in sr)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Predict opponent's likely next step (pursuit_direct-ish): move toward our position.
    p_stage_dx = 0 if ox == sx else (1 if ox < sx else -1)
    p_stage_dy = 0 if oy == sy else (1 if oy < sy else -1)
    pred_ox = ox + p_stage_dx
    pred_oy = oy + p_stage_dy

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_now = cheb(nx, ny, ox, oy)
            d_pred = cheb(nx, ny, pred_ox, pred_oy)

            # Resource bias (if any): pursuer goes toward, evader goes away from nearest resource.
            r_bias = 0
            if isinstance(resources, list) and resources:
                best = None
                for r in resources:
                    if isinstance(r, (list, tuple)) and len(r) >= 2:
                        rx, ry = int(r[0]), int(r[1])
                        if 0 <= rx < w and 0 <= ry < h:
                            dist = cheb(nx, ny, rx, ry)
                            if best is None or dist < best:
                                best = dist
                if best is not None:
                    r_bias = -best if self_pursuer else best

            # Obstacle pressure: penalize moving into positions with fewer valid neighbor cells.
            neigh = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    tx, ty = nx + ax, ny + ay
                    if valid(tx, ty):
                        neigh += 1
            obst_pen = -neigh

            if self_pursuer:
                score = -d_now - 0.6 * d_pred + r_bias + 0.1 * neigh
            else:
                score = d_now + 0.8 * d_pred + r_bias + 0.05 * neigh

            cand.append((score, dx, dy))

    if not cand:
        return [0, 0]

    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(cand[0][1]), int(cand[0][2])]