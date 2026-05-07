def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs_set.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs_set:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (None, -10**9, 0, 0, 0, 0)  # (dx,dy, score, tx,ty, oppd)

    oppd_all = cheb(sx, sy, ox, oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh) or (nx, ny) in obs_set:
            continue

        best_res_score = -10**9
        best_tx_ty = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)

            # Prefer resources we can reach strictly earlier; otherwise still take likely-but-secondary targets.
            adv = od - sd  # positive means we are closer than opponent
            # Small tie-break to prefer closer resources and stable ordering.
            score = 1000 * (1 if adv > 0 else 0) + adv * 10 - sd - (0.01 * cheb(nx, ny, ox, oy))
            if score > best_res_score or (score == best_res_score and (rx, ry) < best_tx_ty):
                best_res_score = score
                best_tx_ty = (rx, ry)

        if best_tx_ty is None:
            continue

        rx, ry = best_tx_ty
        sd_now = cheb(nx, ny, rx, ry)
        od_now = cheb(ox, oy, rx, ry)
        # Encourage not getting trapped near opponent when not winning the race.
        trap_pen = 0
        if od_now <= sd_now:
            trap_pen = 2 * cheb(nx, ny, ox, oy) - oppd_all
        final_score = best_res_score - trap_pen

        if (final_score > best_move[1]) or (final_score == best_move[1] and (dx, dy) < (best_move[0] if best_move[0] else (9, 9))):
            best_move = ((dx, dy), final_score, rx, ry, sd_now, od_now)

    dx, dy = best_move[0]
    return [int(dx), int(dy)]