def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        elif isinstance(a, dict) and "x" in a and "y" in a:
            x, y = int(a["x"]), int(a["y"])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Pick a small set of promising targets deterministically
    targets = sorted(resources, key=lambda p: (cheb(sx, sy, p[0], p[1]), p[0], p[1]))[:3]

    best_move = [0, 0]
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        # Prefer moves that reduce our distance to the best "won" target
        for tx, ty in targets:
            my_d = cheb(nx, ny, tx, ty)
            op_d = cheb(ox, oy, tx, ty)
            # Win margin: closer than opponent is strongly preferred
            win_margin = (op_d - my_d)
            # Also lightly prefer absolute closeness for fallback
            score += 200 * (1 if win_margin > 0 else 0) + 20 * win_margin - my_d
            # If we step onto a resource, dominate
            if my_d == 0:
                score += 10000

        # Break ties deterministically by closer to center then lexicographic move
        center_pen = cheb(nx, ny, (w - 1) / 2.0, (h - 1) / 2.0)
        score -= int(center_pen * 3)

        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move