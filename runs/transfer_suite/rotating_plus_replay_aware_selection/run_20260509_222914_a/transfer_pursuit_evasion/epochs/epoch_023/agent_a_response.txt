def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role") or "").lower()
    pursuer = ("purs" in self_role) or ("catch" in self_role) or ("hunter" in self_role)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def free(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def legal_from(px, py):
        out = []
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if free(nx, ny):
                out.append((nx, ny))
        return out if out else [(px, py)]

    if pursuer:
        opp_legal = legal_from(ox, oy)
        best = None
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not free(nx, ny):
                continue
            worst_d = -1
            for ax, ay in opp_legal:
                d = abs(nx - ax) + abs(ny - ay)
                if d > worst_d:
                    worst_d = d
            val = worst_d
            if (best is None) or (val < best[0]) or (val == best[0] and (dx, dy) < best[1]):
                best = (val, (dx, dy))
        if best is not None:
            dx, dy = best[1]
            if (x + dx, y + dy) == (ox, oy):
                return [int(dx), int(dy)]
            return [int(dx), int(dy)]

    # Evader: maximize distance; also prefer moves that increase distance-to-farthest-corner
    legal = legal_from(x, y)
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(ox - c[0]) + abs(oy - c[1]))

    best = None
    for nx, ny in legal:
        d = abs(nx - ox) + abs(ny - oy)
        dc = abs(nx - far_corner[0]) + abs(ny - far_corner[1])
        val = (d, dc)
        move = (nx - x, ny - y)
        if abs(move[0]) > 1 or abs(move[1]) > 1:
            move = (0, 0)
        if (best is None) or (val > best[0]) or (val == best[0] and move < best[1]):
            best = (val, move)

    dx, dy = best[1] if best is not None else (0, 0)
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        dx = 0
        dy = 0
    return [int(dx), int(dy)]