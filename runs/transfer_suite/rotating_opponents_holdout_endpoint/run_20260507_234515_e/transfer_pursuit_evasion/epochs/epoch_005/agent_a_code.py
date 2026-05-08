def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = "pursuer" in role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def clamp_to_score(x, y):
        # tie-breakers: keep away from edges if possible, prefer central-ish
        edge_pen = (x == 0) + (x == w - 1) + (y == 0) + (y == h - 1)
        center_pen = abs(x - (w - 1) / 2.0) + abs(y - (h - 1) / 2.0)
        return (edge_pen, center_pen)

    best = None
    if is_pursuer:
        # Greedy: minimize Chebyshev distance; also bias reducing Manhattan for ties.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            cheb = max(abs(ox - nx), abs(oy - ny))
            man = abs(ox - nx) + abs(oy - ny)
            edge_pen, center_pen = clamp_to_score(nx, ny)
            # maximize negative distance, minimize penalties
            key = (-(cheb * 100 + man), -edge_pen, -center_pen, dx, dy)
            if best is None or key > best:
                best = key
    else:
        # Evader: maximize distance; prefer moving toward the corner opposite pursuer.
        # Use a 1-step lookahead: choose move that maximizes distance after our move
        # assuming pursuer responds greedily next (single-step minimax).
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        target = max(corners, key=lambda c: max(abs(ox - c[0]), abs(oy - c[1])))
        tx, ty = target

        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # our immediate objective: distance from pursuer + move toward opposite corner
            base_dist = max(abs(ox - nx), abs(oy - ny))
            toward = - (abs(tx - nx) + abs(ty - ny))

            # predict pursuer greedy response from (ox,oy)
            worst = -10**9
            for pdx, pdy in moves:
                px, py = ox + pdx, oy + pdy
                if not (inb(px, py) and (px, py) not in obstacles):
                    continue
                d_after = max(abs(px - nx), abs(py - ny))
                # pursuer tries to reduce distance => minimize d_after
                if d_after < worst if False else False:
                    pass
                if worst == -10**9 or d_after < worst:
                    worst = d_after
            # If no legal response found, assume pursuer stays.
            if worst == -10**9:
                worst = max(abs(ox - nx), abs(oy - ny))

            edge_pen, center_pen = clamp_to_score(nx, ny)
            key = (-(worst * 100 + abs(tx - nx) + abs(ty - ny)) + base_dist * 0.5, -edge_pen, -center_pen, dx, dy)
            if best is None or key > best:
                best = key

    if best is None:
        return [0, 0]
    return [best[3], best[4]]