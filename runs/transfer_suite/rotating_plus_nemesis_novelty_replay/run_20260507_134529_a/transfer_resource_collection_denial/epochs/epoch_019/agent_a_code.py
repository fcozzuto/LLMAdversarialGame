def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def best_key_for_move(nx, ny):
        best_adv = -10**9  # opd-myd (higher is better)
        best_myd = 10**9
        best_minstack = 10**9  # min gap (myd-opd), smaller is better when we can't overtake
        min_gap = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            gap = myd - opd
            if adv > best_adv or (adv == best_adv and myd < best_myd):
                best_adv, best_myd = adv, myd
            if gap < min_gap:
                min_gap = gap
        # If we can be closer to some resource (best_adv>0), prioritize that.
        # Otherwise, reduce the opponent's lead by minimizing min_gap (closest "contest").
        if best_adv > 0:
            return (0, -best_adv, best_myd, nx, ny)  # maximize adv => minimize -adv
        else:
            return (1, min_gap, best_myd, nx, ny)  # minimize gap

    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0
        key = best_key_for_move(nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]