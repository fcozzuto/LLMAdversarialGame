def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_lead = None
    best_any = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        diff = od - sd
        if best_lead is None or diff > best_lead[0] or (diff == best_lead[0] and sd < best_lead[1]):
            best_any = (diff, sd, od, rx, ry)
        if diff > 0:
            if best_lead is None or diff > best_lead[0] or (diff == best_lead[0] and sd < best_lead[1]):
                best_lead = (diff, sd, od, rx, ry)

    _, _, _, tx, ty = best_lead if best_lead is not None else best_any

    # If opponent is closer, try to "shadow": move to reduce opponent's progress while keeping pressure on target.
    opp_closer = cheb(ox, oy, tx, ty) < cheb(sx, sy, tx, ty)

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        d_opp_after = cheb(nx, ny, ox, oy)  # separation proxy
        # Primary: improve our distance to target
        score = -d_to
        # Secondary: if we lead, also keep away; if we lag, maximize separation from opponent while still approaching.
        if opp_closer:
            score += (0.6 * d_opp_after)
            # And slightly prefer moves that increase opponent's distance to target (indirect via blocking)
            score += (0.2 * (-abs(cheb(ox, oy, tx, ty) - cheb(nx, ny, tx, ty))))
        else:
            score += (0.4 * d_opp_after)
        # Tertiary: deterministic tie-break toward central-ish and minimal distance to target
        score = (score, -cheb(nx, ny, gw//2, gh//2), -d_to, dx, dy)

        if best is None or score > best:
            best = score

    return [int(best[3]), int(best[4])]