def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    best_rx, best_ry = None, None
    best_score = -10**18
    for r in resources:
        rx, ry = r[0], r[1]
        myd = abs(sx - rx) + abs(sy - ry)
        opd = abs(ox - rx) + abs(oy - ry)
        # Prefer resources we can reach no later than opponent; otherwise prefer biggest reach gap.
        score = (opd - myd) * 1000 - myd
        if myd <= opd:
            score += 50000
        if score > best_score:
            best_score = score
            best_rx, best_ry = rx, ry

    dx0 = 0
    dy0 = 0
    if best_rx > sx:
        dx0 = 1
    elif best_rx < sx:
        dx0 = -1
    if best_ry > sy:
        dy0 = 1
    elif best_ry < sy:
        dy0 = -1

    if abs(best_rx - sx) >= abs(best_ry - sy):
        return [dx0, 0] if dx0 != 0 else [0, dy0]
    else:
        return [0, dy0] if dy0 != 0 else [dx0, 0]