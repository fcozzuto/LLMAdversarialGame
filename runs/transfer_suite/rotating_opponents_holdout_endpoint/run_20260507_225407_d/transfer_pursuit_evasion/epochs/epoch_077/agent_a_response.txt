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
    is_evader = ("evad" in role) or ("escape" in role) or ("runner" in role)
    is_pursuer = not is_evader

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    # Prefer diagonals and directions toward/away from opponent deterministically via scoring.
    moves = []
    if is_pursuer:
        for dx in dxs:
            for dy in dys:
                if dx == 0 and dy == 0: continue
                nx, ny = sx + dx, sy + dy
                if blocked(nx, ny): continue
                moves.append((cheb(nx, ny, ox, oy), nx, ny, dx, dy))
        if not moves:
            cand = [(sx, sy, 0, 0)]
        else:
            moves.sort(key=lambda t: (t[0], -t[1], -t[2]))
            best = moves[0]
            return [best[3], best[4]]
    # Evader: move to increase distance; if possible, bias toward farthest corner.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    best_score = -10**9
    best_move = [0, 0]
    for dx in dxs:
        for dy in dys:
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): continue
            d_opp = cheb(nx, ny, ox, oy)
            d_corner = cheb(nx, ny, far_corner[0], far_corner[1])
            # Score: maximize distance from pursuer, then maximize distance from target corner? (Prefer reaching far corner)
            score = d_opp * 10 + d_corner
            # Tie-break: prefer moves that change x then y deterministically
            score += (1 if dx > 0 else 0) + (1 if dy > 0 else 0) * 0.01
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    return best_move