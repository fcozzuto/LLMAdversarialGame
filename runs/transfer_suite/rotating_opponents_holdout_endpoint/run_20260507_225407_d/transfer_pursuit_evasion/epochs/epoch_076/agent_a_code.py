def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles or not inb(x, y)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escape" in role) or ("runner" in role) or ("target" not in role and "purs" not in role and "hunter" not in role)
    is_pursuer = not is_evader

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break order preference: favor cardinal moves over diagonals, then positive x, then positive y.
    pref = {(-1, -1): 5, (0, -1): 3, (1, -1): 6, (-1, 0): 2, (0, 0): 1, (1, 0): 0, (-1, 1): 4, (0, 1): 7, (1, 1): 8}

    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        # Obstacle risk: count adjacent obstacles (including diagonals); being adjacent is often worse for pursuit/evasion.
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj += 1

        d = cheb(nx, ny, ox, oy)
        # If evader: maximize distance; if pursuer: minimize distance (while avoiding obstacles).
        base = d if is_evader else -d

        # Push toward corners only when it doesn't reduce distance too much (deterministic fallback).
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        corner_dist = min(cheb(nx, ny, cx, cy) for cx, cy in corners)
        corner_term = -corner_dist if is_evader else corner_dist

        score = base * 10 - adj * 3 + corner_term

        if best_score is None or score > best_score or (score == best_score and pref[(dx, dy)] < pref[tuple(best_move)]):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]