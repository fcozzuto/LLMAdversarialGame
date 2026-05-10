def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def clamp_move(nx, ny):
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return True
        return False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose a move that maximizes "can I beat opponent to a resource?" and avoids obstacles.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        total = 0
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            # Beat opponent to the same cell first; prefer smallest d_me among winning targets.
            if d_me == 0:
                total += 10_000_000
            if d_me < d_op:
                total += (d_op - d_me + 1) * 100_000 - d_me
            elif d_me == d_op:
                total += 50_000 - d_me
            else:
                total -= (d_me - d_op + 1) * 10_000 + d_me

            # Small preference for overall closeness (keeps progress).
            total += max(0, 30 - d_me)

        if best_score is None or total > best_score:
            best_score = total
            best_move = (dx, dy)
        elif total == best_score:
            # Deterministic tie-break: smallest |dx|+|dy| then lexicographic.
            if (abs(dx) + abs(dy), dx, dy) < (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1]):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]