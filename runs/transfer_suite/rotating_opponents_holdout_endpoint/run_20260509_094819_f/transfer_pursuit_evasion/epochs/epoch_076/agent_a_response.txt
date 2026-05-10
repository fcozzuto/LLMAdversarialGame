def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Prefer evasion: maximize distance; avoid moving onto opponent.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(sx, sy, c[0], c[1]))
    fx, fy = far_corner

    best_val = -10**9
    best = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in blocked:
            continue
        d_to_opp = cheb(nx, ny, ox, oy)
        # If we step onto opponent, that's immediate capture; heavily avoid.
        if nx == ox and ny == oy:
            val = -10**12
        else:
            # Also encourage moving toward our farthest corner to keep distance.
            dist_corner = cheb(nx, ny, fx, fy)
            # Small deterministic bias toward diagonal/forward-ish moves to break ties.
            bias = (1 if abs(dx) + abs(dy) == 2 else 0) + (1 if dx == 0 and dy == 0 else 0)
            val = d_to_opp * 1000 + dist_corner * 3 - bias
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]