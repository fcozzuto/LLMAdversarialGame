def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)
    turns_remaining = int(observation.get("turns_remaining", 0) or 0)

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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Prefer targets we can reach no later than opponent; otherwise pick best "gain"
    best_target = None
    best_val = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Encourage being ahead; also prefer closer targets when tied.
        lead = od - sd
        within = 1 if (turns_remaining == 0 or sd <= turns_remaining) else 0
        val = (within, lead, -sd)
        if best_val is None or val > best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target

    # Choose the move that improves lead over the opponent (assume opponent can reduce distance by at most 1 per turn)
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh) or (nx, ny) in obs_set:
            continue
        self_d_after = cheb(nx, ny, tx, ty)
        opp_d_now = cheb(ox, oy, tx, ty)
        # Opponent likely can reduce by 1; keep a slight conservative assumption.
        opp_d_assumed = opp_d_now - 1 if opp_d_now > 0 else 0
        lead_after = opp_d_assumed - self_d_after
        score = (lead_after, -self_d_after, -abs(nx - tx) - abs(ny - ty))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]