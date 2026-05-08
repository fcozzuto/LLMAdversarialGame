def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    turns_remaining = observation.get("turns_remaining", 0)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    best = None
    for dx, dy, nx, ny in cand:
        best_for_this_move = -10**9
        for tx, ty in res:
            sd = dist((nx, ny), (tx, ty))
            od = dist((ox, oy), (tx, ty))

            # Prefer resources we can beat (or at least reach no later than opponent),
            # with urgency based on remaining turns.
            beat_margin = (od - sd)  # positive if we arrive first
            urgency = min(turns_remaining, sd)
            # If both can reach, earlier is better; if we can't, penalize heavily.
            reach_pen = 0
            if sd > turns_remaining:
                reach_pen -= 200
            if od > turns_remaining and sd <= turns_remaining:
                reach_pen += 30

            val = 1000 * beat_margin + 3 * (turns_remaining - sd) - 1.5 * sd + reach_pen
            # Tie-break: prefer closer to avoid getting stuck near obstacles
            if val > best_for_this_move:
                best_for_this_move = val
        if best is None or best_for_this_move > best[0]:
            best = (best_for_this_move, dx, dy)
    return [best[1], best[2]]