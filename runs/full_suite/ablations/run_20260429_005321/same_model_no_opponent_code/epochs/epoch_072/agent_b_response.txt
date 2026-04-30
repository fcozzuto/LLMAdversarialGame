def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Pick a resource where we have the biggest distance advantage over opponent.
    best_t = None
    best_adv = None
    for rx, ry in resources:
        my = d2(sx, sy, rx, ry)
        opd = d2(ox, oy, rx, ry)
        adv = opd - my  # positive means we are closer
        key = (adv, -rx, -ry)  # deterministic tie-break
        if best_adv is None or key > (best_adv[0], best_adv[1], best_adv[2]):
            best_adv = (adv, -rx, -ry)
            best_t = (rx, ry)

    # If no resources, head toward the center while staying away from opponent.
    if best_t is None:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not valid(nx, ny):
                    continue
                score = d2(nx, ny, cx, cy) - 2 * d2(nx, ny, ox, oy)
                if best is None or score < best[0]:
                    best = (score, dx, dy)
        return [int(best[1]), int(best[2])] if best is not None else [0, 0]

    rx, ry = best_t

    # One-step evaluation: go closer to target, avoid stepping onto opponent-near cells, prefer safety.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            my_to_t = d2(nx, ny, rx, ry)
            my_to_opp = d2(nx, ny, ox, oy)
            opp_to_t = d2(ox, oy, rx, ry)
            # If opponent is closer to target, reduce contest by pushing away; else race to target.
            my_vs_opp_now = d2(sx, sy, rx, ry) - d2(ox, oy, rx, ry)
            chase = 1.0 if my_vs_opp_now <= 0 else 0.6
            score = chase * my_to_t + 0.8 * (1.0 / (1.0 + my_to_opp)) * 10 - 0.25 * opp_to_t
            # Strongly avoid being adjacent (heuristic "block" prevention).
            if my_to_opp <= 1:
                score += 50
            # If we'd land on a resource, reward it decisively.
            if (nx, ny) in resources:
                score -= 100
            candidates.append((score, dx, dy))

    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])] if candidates else [0, 0]