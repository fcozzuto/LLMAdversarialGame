def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(x, y):
        if x < 0: x = 0
        if y < 0: y = 0
        if x >= w: x = w - 1
        if y >= h: y = h - 1
        return x, y

    my = (sx, sy)
    opp = (ox, oy)

    if not resources:
        return [0, 0]

    # Pick best target via "advantage" and "race" (different from purely md-0.95*od).
    best = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        md = dist(my, (rx, ry))
        od = dist(opp, (rx, ry))
        # Race-first: prefer resources where we are not much later; otherwise only if we can deny near-ties.
        # Higher advantage + smaller time is better; we minimize negative/positive via tuple below.
        advantage = od - md  # positive means we are closer
        race_score = max(md - od, 0) * 3 + md  # penalize being later
        if advantage >= 0:
            key = (0, race_score, md)
        else:
            # If opponent is closer, try to "deny": pick where gap is small enough.
            key = (1, race_score + (-advantage) * 0.5, -advantage)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    target = best[1] if best else resources[0]

    tx, ty = target
    # One-step lookahead: choose move maximizing our progress to target while discouraging giving opponent an easy pickup.
    cand = []
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        nd_my = dist((nx, ny), (tx, ty))
        cur_md = dist(my, (tx, ty))
        improvement = cur_md - nd_my
        # "Deny pressure": prefer moves that reduce our distance without increasing how close we stay to opponent's likely race.
        nd_opp_to_target = dist(opp, (tx, ty))
        # If we're moving away, improvement becomes negative; penalize.
        score = (-improvement, nd_my, nd_opp_to_target)  # minimize
        cand.append((score, [dx, dy]))
    if not cand:
        return [0, 0]
    cand.sort(key=lambda x: x[0])
    return cand[0][1]