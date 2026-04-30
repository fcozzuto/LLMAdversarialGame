def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Move toward center while avoiding obstacles
        tx, ty = (W - 1) // 2, (H - 1) // 2
        best = None
        best_d = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
                d = abs(nx - tx) + abs(ny - ty)
                if best_d is None or d < best_d:
                    best_d = d
                    best = (dx, dy)
        return list(best if best is not None else (0, 0))

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    # Pre-rank targets by advantage and closeness
    ranked = []
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        advantage = od - sd  # larger is better
        ranked.append((rx, ry, advantage, sd))
    ranked.sort(key=lambda t: (-t[2], t[3], t[1], t[0]))

    best_move = (0, 0)
    best_score = None
    # Evaluate moves by how they change our best reachable target advantage
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            continue
        # Consider top few ranked targets for speed/determinism
        score = None
        for i in range(6 if len(ranked) > 6 else len(ranked)):
            rx, ry, _, _ = ranked[i]
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            # Maximize: advantage first, then minimize sd, then deterministic tie by coords
            cand = (adv, -sd, -ry, -rx)
            if score is None or cand > score:
                score = cand
        if score is None:
            continue
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]