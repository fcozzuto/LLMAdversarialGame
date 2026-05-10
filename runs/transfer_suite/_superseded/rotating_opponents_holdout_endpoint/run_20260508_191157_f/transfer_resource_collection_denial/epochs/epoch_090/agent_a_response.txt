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

    # Target: maximize contest likelihood (opponent's closeness helps us decide what to race for).
    best_res = None
    best_key = None
    for rx, ry in resources:
        md = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        # Prefer resources opponent is close to (we must respond), but also where we are not hopeless.
        # Larger key is better.
        key = ((-od, -md), (od - md), -(md + 2 * (od <= 1)))
        # Flatten compare deterministically
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        myd = abs(tx - nx) + abs(ty - ny)
        # Opponent position assumed unchanged for this move evaluation.
        opd = abs(tx - ox) + abs(ty - oy)

        # Also consider proximity to any resource to avoid dead ends.
        nearest_my = None
        nearest_adv = None
        for rx, ry in resources:
            md = abs(rx - nx) + abs(ry - ny)
            od = abs(rx - ox) + abs(ry - oy)
            adv = od - md
            if nearest_my is None or md < nearest_my:
                nearest_my = md
            if nearest_adv is None or adv > nearest_adv:
                nearest_adv = adv

        score = 0
        if myd == 0:
            score += 1000
        score += (opd - myd) * 10
        score += (nearest_adv if nearest_adv is not None else 0) * 2
        score -= myd * 0.5
        score -= (0.1 if dx == 0 and dy == 0 else 0)

        key = (score, -nearest_my if nearest_my is not None else 0, dx, dy)
        if best_score is None or key > best_score:
            best_score = key
            best_move = [dx, dy]

    return best_move