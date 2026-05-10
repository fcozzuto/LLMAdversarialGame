def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_in = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    center_x, center_y = w // 2, h // 2

    best_move = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            nx, ny = sx, sy
        if (nx, ny) in obstacles:
            nx, ny = sx, sy

        best_adv = -10**9
        best_my_d = 10**9
        best_opp_d = 10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - my_d
            if adv > best_adv or (adv == best_adv and my_d < best_my_d) or (adv == best_adv and my_d == best_my_d and opp_d < best_opp_d):
                best_adv, best_my_d, best_opp_d = adv, my_d, opp_d

        # Prefer higher advantage, then smaller distance to target, then closer to center
        key = (-(best_adv), best_my_d, cheb(nx, ny, center_x, center_y), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move