def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    target = None
    if resources:
        bestd = None
        for rx, ry in resources:
            d = dist2(x, y, rx, ry)
            if bestd is None or d < bestd or (d == bestd and (rx, ry) < target):
                bestd = d
                target = (rx, ry)

    # Heuristic: if resources exist, go to best target but also push away from opponent (deny contest)
    # and avoid getting adjacent to obstacles.
    best_move = None
    best_score = None
    for dx, dy, nx, ny in cand:
        score = 0
        if target is not None:
            rx, ry = target
            score -= dist2(nx, ny, rx, ry)
            # If multiple resources, prefer progressing toward the furthest resource in that direction
            # (helps prevent getting stuck behind obstacles).
            best_prog = None
            for sx, sy in resources:
                if sx == nx and sy == ny:
                    continue
                prog = (sx - nx) * (rx - nx) + (sy - ny) * (ry - ny)
                if best_prog is None or prog > best_prog:
                    best_prog = prog
            if best_prog is not None:
                score += 0.01 * best_prog
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            score -= dist2(nx, ny, cx, cy)

        # Deny opponent: prefer moves that increase distance to opponent
        score += 0.05 * dist2(nx, ny, ox, oy)

        # Obstacle proximity penalty (prefer moving away from dense obstacle areas)
        adj = 0
        for oxp, oyp in obstacles:
            if abs(oxp - nx) <= 1 and abs(oyp - ny) <= 1:
                adj += 1
        score -= 0.2 * adj

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

        # Deterministic tie-break
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]