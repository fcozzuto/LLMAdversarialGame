def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    pref = {(0, 0): 0, (0, 1): 1, (0, -1): 2, (1, 0): 3, (-1, 0): 4, (1, 1): 5, (-1, -1): 6, (1, -1): 7, (-1, 1): 8}

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("escape" in role) or ("hide" in role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best_move = (0, 0)
    if is_evader:
        best = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            d_op = cheb(nx, ny, ox, oy)
            # Heuristic: maximize distance to pursuer, and also progress to farthest corner.
            d_corner = cheb(nx, ny, far_corner[0], far_corner[1])
            # Penalty if this move would reduce distance too much compared to staying.
            d_here = cheb(sx, sy, ox, oy)
            score = (d_op * 10) + (-d_corner) + (d_op - d_here)
            if score > best or (score == best and pref[(dx, dy)] < pref[best_move]):
                best = score
                best_move = (dx, dy)
    else:
        best = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            # Heuristic: minimize distance; avoid moves that "waste" time via staying if alternatives exist.
            score = d * 100 + (pref[(dx, dy)] if (dx, dy) != (0, 0) else 1000)
            if score < best or (score == best and pref[(dx, dy)] < pref[best_move]):
                best = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]