def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If resources missing, just avoid obstacles while slightly moving toward opponent to disrupt.
    if not resources:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, ox, oy)
            key = (d, dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    best_key = None
    best_move = (0, 0)

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        # Choose the resource that gives us the largest distance advantage over the opponent next.
        best_adv = -10**9
        best_my_d = 10**9
        best_opp_d = 10**9
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - my_d  # higher => more likely we grab first
            if adv > best_adv or (adv == best_adv and (my_d < best_my_d or (my_d == best_my_d and opp_d < best_opp_d))):
                best_adv, best_my_d, best_opp_d = adv, my_d, opp_d

        # Tie-break: prefer closer-to-resource moves that keep some distance from opponent (avoid sharing race).
        opp_step_d = cheb(nx, ny, ox, oy)
        edge_bonus = 0.05 if (nx in (0, w - 1) or ny in (0, h - 1)) else 0.0

        key = (-best_adv, best_my_d, -opp_step_d, edge_bonus, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]