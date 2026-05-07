def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate move by the best resource we can plausibly out-collect.
        # Prefer resources where we are closer than opponent, and penalize moving away.
        move_score = -10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            rel = od - sd  # positive means we are closer
            # Encourage immediate capture/near capture.
            cap_bonus = 0
            if sd == 0: cap_bonus += 1000
            elif sd == 1: cap_bonus += 200
            # Small preference for shortening our distance even if opponent also gets it.
            approach = -sd
            # Mild obstacle-adjacency deterrent (encourage maneuvering).
            adj_pen = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in obstacles:
                        adj_pen += 2
            s = 50 * rel + cap_bonus + approach - adj_pen
            if s > move_score:
                move_score = s

        if best_score is None or move_score > best_score:
            best_score = move_score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]