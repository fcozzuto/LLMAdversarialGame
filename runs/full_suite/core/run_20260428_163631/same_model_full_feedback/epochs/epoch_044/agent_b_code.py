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

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def manh(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = 10**18

    # deterministic tie-breaker order: keep order in moves
    center = (w // 2, h // 2)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            # Pick resource that best improves our advantage vs opponent
            cur_best = 10**18
            for rx, ry in resources:
                d_our = manh(nx, ny, rx, ry)
                d_opp = manh(nx, ny, ox, oy) + 0  # baseline to encourage general suppression
                # Advantage: smaller our distance than opponent would be.
                # Also prefer moving toward a resource where we are relatively closer than opponent.
                d_opp_res = manh(ox, oy, rx, ry)
                adv = d_our - d_opp_res
                # Lower score is better; weights tuned deterministically
                score = adv * 3 + d_our + d_opp * 0.1
                if score < cur_best:
                    cur_best = score
            score_here = cur_best
        else:
            score_here = manh(nx, ny, center[0], center[1])

        # Small penalty for moving closer to opponent (helps reduce races) unless capturing resource proximity
        if resources:
            score_here += 0.05 * manh(nx, ny, ox, oy)
        else:
            score_here += 0.1 * manh(nx, ny, ox, oy)

        if score_here < best_score:
            best_score = score_here
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best