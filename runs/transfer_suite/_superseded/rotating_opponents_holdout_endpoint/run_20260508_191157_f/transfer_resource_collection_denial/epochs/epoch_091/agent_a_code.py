def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set((x, y) for x, y in obstacles)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick target resource: prefer those where opponent is closer than us (must contest),
    # but keep overall path quality and break ties deterministically.
    best_r = None
    best_key = None
    for rx, ry in resources:
        md = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        # Higher key is better.
        key = (od - md, -(md + 2 * (md == 0)), -(rx * 9 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))

    # If somehow no legal move (shouldn't happen), stay.
    if not legal:
        return [0, 0]

    # Evaluate next step: maximize improvement toward target, penalize moving away,
    # and slightly prefer reducing opponent's potential distance to that same target.
    best_m = None
    best_m_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        myd = abs(tx - nx) + abs(ty - ny)
        myd_now = abs(tx - sx) + abs(ty - sy)
        oppd_now = abs(tx - ox) + abs(ty - oy)
        # Opponent doesn't move this turn; use their current distance as pressure term.
        # If we get significantly closer, we increase contest chance.
        key = (-(myd), (myd_now - myd), -(oppd_now - myd), -(dx * 3 + dy))
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]