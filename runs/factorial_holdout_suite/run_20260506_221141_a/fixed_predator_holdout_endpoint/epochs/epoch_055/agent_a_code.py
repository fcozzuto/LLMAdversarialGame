def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
        except Exception:
            pass
    if not resources:
        return [0, 0]

    def kd(a, b):
        ax, ay = a
        bx, by = b
        dx, dy = abs(ax - bx), abs(ay - by)
        return dx if dx > dy else dy

    # Rank resources: prefer where we are closer than opponent, and where the race "margin" is big.
    ranked = []
    for t in resources:
        sd = kd((sx, sy), t)
        od = kd((ox, oy), t)
        margin = od - sd  # positive means we race ahead
        # Prefer farther-away (less likely to be immediately taken) if margin is equal
        s = margin * 1000 - sd
        ranked.append((s, t))
    ranked.sort(key=lambda z: (z[0], -z[1][0], -z[1][1]), reverse=True)
    top = [t for _, t in ranked[: min(4, len(ranked))]]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))
    # Deterministic iteration order: prioritize horizontal/vertical progress slightly
    moves.sort(key=lambda m: (abs(m[0]) + abs(m[1]) == 0, abs(m[1]), abs(m[0]), m[0], m[1]))

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine would keep us; align scoring

        # Evaluate by best target we can secure next; also mildly reduce opponent threat.
        score = -10**18
        for t in top:
            sd2 = kd((nx, ny), t)
            od2 = kd((ox, oy), t)
            margin2 = od2 - sd2
            # If opponent is very close, penalize (denier behavior); otherwise race more aggressively.
            danger = 3 - (od2 if od2 < 3 else 3)  # 0..3
            cur = margin2 * 1200 - sd2 * 3 - danger * 25
            if cur > score:
                score = cur

        # Small tiebreak: prefer moves that head toward center to avoid deadlocks
        cx, cy = w // 2, h // 2
        center = -(abs(nx - cx) + abs(ny - cy))
        score = score + center * 0.01 - (abs(dx) + abs(dy)) * 0.001

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]