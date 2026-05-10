def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obstacles = set()
    for it in (observation.get("obstacles") or []):
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic priority: sort by (dx,dy) after valid filtering by scoring only.
    move_order = sorted(moves, key=lambda m: (m[0], m[1]))

    best_move = (0, 0)
    best_score = None

    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        # If closer is good (pursuer), minimize d; if farther is good (evader), maximize d.
        score = d if is_evader else -d

        # Prefer staying away from nearest obstacle (more important for evader).
        if obstacles:
            mind = 10**9
            for (oxb, oyb) in obstacles:
                dd = cheb(nx, ny, oxb, oyb)
                if dd < mind:
                    mind = dd
            if is_evader:
                score += 0.2 * mind
            else:
                score += 0.05 * mind

        # Gentle preference to avoid edges for evader (unless already near optimal corner).
        if is_evader:
            edge_pen = (0 if 1 <= nx <= w - 2 else 1) + (0 if 1 <= ny <= h - 2 else 1)
            score -= 0.15 * edge_pen

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]