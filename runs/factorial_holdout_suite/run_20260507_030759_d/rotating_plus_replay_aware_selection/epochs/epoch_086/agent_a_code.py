def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    if not resources or w <= 0 or h <= 0:
        return [0, 0]

    scored = {}
    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue
        best = -10**18
        # Prefer resources where we can beat (or tie) opponent; otherwise minimize opponent advantage.
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(nsx, nsy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Collecting soon matters more early; last turns less about chasing.
            t = observation.get("turns_remaining", 0)
            urgency = 1.0 + (t / 100.0)
            beat = (od - sd)  # positive if we are closer
            # Extra boost if we can reach immediately and force near-term control.
            immediate = 6.0 if sd == 0 else (2.0 if sd == 1 else 0.0)
            # Penalize being too slow even if beating by a bit.
            slow_pen = -0.35 * sd
            # If opponent is already much closer, strongly discourage.
            opp_pen = 0.0 if beat >= 0 else -2.5 * (-beat)
            val = (beat * urgency) + immediate + slow_pen + opp_pen
            if val > best:
                best = val
        # Tie-break: move that increases distance from opponent slightly (reduces interference risk).
        dist_away = cheb(nsx, nsy, ox, oy) - cheb(sx, sy, ox, oy)
        best += 0.1 * dist_away
        scored[(mdx, mdy)] = best

    if not scored:
        return [0, 0]
    # Deterministic argmax with fixed move ordering
    order = moves
    best_move = order[0]
    best_val = -10**18
    for m in order:
        if m in scored and scored[m] > best_val:
            best_val = scored[m]
            best_move = m
    return [int(best_move[0]), int(best_move[1])]