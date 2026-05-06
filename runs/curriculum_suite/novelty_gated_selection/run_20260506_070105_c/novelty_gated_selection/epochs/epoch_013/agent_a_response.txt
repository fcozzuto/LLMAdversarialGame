def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obstacles_raw)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose best "swing" resource to aim for: maximize (opp_d - my_d) and closeness.
    best_target = resources[0]
    best_key = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        key = (-(opd - myd), myd, rx, ry)  # smallest key => largest advantage
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    # Score each move by how much it improves winning chances for the top few resources.
    # Weight advantages more when move reduces my distance.
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        scored = 0
        # Compute per-resource advantage with distance shaping.
        # Use only top-3 by current advantage magnitude for robustness and speed.
        advs = []
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            adv = opd - myd
            advs.append((adv, myd, rx, ry))
        advs.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
        for adv, myd, _, _ in advs[:3]:
            # If adv is positive, we are likely to reach first; extra reward for getting nearer.
            # If adv negative, strongly discourage moves that worsen our position against opponent.
            scored += (adv * 6) - (myd * 1.5)
        # Additional shaping: move toward chosen target, but don't walk into being worse vs all.
        tx, ty = best_target
        scored += (man(sx, sy, tx, ty) - man(nx, ny, tx, ty)) * 2.0
        cand.append((scored, dx, dy, nx, ny))

    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [cand[0][1], cand[0][2]]