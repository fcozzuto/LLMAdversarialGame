def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role") or "")
    pursuer = ("purs" in role.lower()) or (role.lower() == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def d_cheb(x, y):
        dx = x - ox
        dy = y - oy
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def d_man(x, y):
        dx = x - ox
        dy = y - oy
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    # Prefer corners for evasion; prefer center-ish for pursuit to avoid getting boxed by obstacles.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_score(x, y):
        best = -10**9
        for cx, cy in corners:
            dx = cx - x
            dy = cy - y
            if dx < 0: dx = -dx
            if dy < 0: dy = -dy
            best = best if best > (dx + dy) else (dx + dy)
        return best

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        dc = d_cheb(nx, ny)
        dm = d_man(nx, ny)

        if pursuer:
            # Strongly reduce distance; also avoid letting opponent be even safer by not increasing Chebyshev too much.
            val = -dc * 1000 - dm
            # Tie-break toward staying away from edges if obstacle layout can trap.
            edge = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
            val += edge
            # Penalize moves that increase distance from opponent too much.
            cur_dc = d_cheb(sx, sy)
            if dc > cur_dc:
                val -= (dc - cur_dc) * 50
        else:
            # Increase distance; avoid moving adjacent to opponent (capture ends).
            val = dc * 1000 + dm
            adj = 1 if dm <= 1 else 0
            val -= adj * 2000
            # Choose among far regions/corners deterministically.
            val += corner_score(nx, ny) * 2
            # Slightly prefer moves that keep us near a boundary (harder lines to pursue through).
            val += min(nx, ny, (w - 1) - nx, (h - 1) - ny) * (-1)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]