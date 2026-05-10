def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def open_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    def best_response(nx, ny):
        # Deterministic greedy: pursuer minimizes distance; evader maximizes distance
        best = None
        best_val = None
        for dx2, dy2 in moves:
            ex2, ey2 = ox + dx2, oy + dy2
            if not valid(ex2, ey2):
                continue
            d = manh(nx, ny, ex2, ey2)
            # tie-break uses more open neighbors for the mover
            if i_am_evader:
                # opponent is pursuer
                val = (-d, -open_neighbors(ex2, ey2))
            else:
                # opponent is evader
                val = (d, open_neighbors(ex2, ey2))
            if best is None or val < best_val if not i_am_evader else val > best_val:
                best = (ex2, ey2)
                best_val = val
        if best is None:
            return ox, oy
        return best[0], best[1]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        rx, ry = best_response(nx, ny)
        d = manh(nx, ny, rx, ry)

        # Additional obstacle-aware pressure: avoid getting boxed by preferring more open neighbors.
        on = open_neighbors(nx, ny)
        if i_am_evader:
            score = (d, on)
            better = best_score is None or score > best_score
        else:
            score = (-d, on)
            better = best_score is None or score > best_score
        if better:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]