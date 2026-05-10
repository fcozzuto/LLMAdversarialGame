def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "flee"))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def blocked(x, y):
        return (x, y) in obstacles or x < 0 or x >= w or y < 0 or y >= h

    def adj_blocked_count(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if blocked(x + dx, y + dy):
                    c += 1
        return c

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best = None

    cur_dist = abs(sx - ox) + abs(sy - oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        ab = adj_blocked_count(nx, ny)
        # Encourage evader to run; discourage entering cramped areas.
        # Pursuer moves toward target; prefer positions with fewer surrounding blocks.
        if is_evader:
            score = (d * 4) - (ab * 0.7) - (0.35 if d < cur_dist else 0.0)
            # Also avoid moving adjacent to obstacles too much unless it increases distance.
            if ab >= 6 and d <= cur_dist:
                score -= 3.0
        else:
            score = (-d * 4) - (ab * 0.45)
            if d > cur_dist:
                score -= 1.0
        # Deterministic tie-breakers: prefer higher/lower distance accordingly, then lexicographic move.
        if best is None or score > best:
            best = score
            best_move = (dx, dy)
        elif score == best:
            if is_evader:
                if d > (abs((sx + best_move[0]) - ox) + abs((sy + best_move[1]) - oy)):
                    best_move = (dx, dy)
                elif d == (abs((sx + best_move[0]) - ox) + abs((sy + best_move[1]) - oy)) and (dx, dy) < best_move:
                    best_move = (dx, dy)
            else:
                if d < (abs((sx + best_move[0]) - ox) + abs((sy + best_move[1]) - oy)):
                    best_move = (dx, dy)
                elif d == (abs((sx + best_move[0]) - ox) + abs((sy + best_move[1]) - oy)) and (dx, dy) < best_move:
                    best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]