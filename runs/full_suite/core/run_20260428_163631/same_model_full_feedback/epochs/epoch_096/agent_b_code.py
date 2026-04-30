def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]
    if (sx, sy) in set(resources):
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Anticipate opponent: they prefer closest resource to themselves.
    opp_target = None
    best_do = None
    for rx, ry in resources:
        do = cheb(ox, oy, rx, ry)
        if best_do is None or do < best_do or (do == best_do and (rx + ry) < (opp_target[0] + opp_target[1])):
            best_do = do
            opp_target = (rx, ry)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Greedy one-step: move that best improves "prevent opponent from getting their target soon"
    # while still advancing toward resources we can beat.
    best_move = (0, 0)
    best_score = None
    cur_adv_to_best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        # Primary: reduce opponent's lead on their likely target.
        if opp_target is not None:
            rx, ry = opp_target
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            score += 1000 * (do - ds)  # bigger means we close the gap

        # Secondary: choose among resources to either capture soon or deny.
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gap = do - ds  # positive if we're closer
            # Encourage taking if reachable now/soon; discourage leaving them unchallenged.
            score += 40 * gap
            if ds == 0:
                score += 5000
            elif ds <= 2 and gap >= 0:
                score += 200

        # Tiebreak: prefer staying closer to center to avoid getting trapped behind obstacles.
        cx, cy = w // 2, h // 2
        dist_center = cheb(nx, ny, cx, cy)
        score -= dist_center

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]