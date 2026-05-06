def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, cx, cy)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = legal[0]
    best_val = 10**18

    # Race/deny heuristic: favor resources where we are currently closer, and moves that keep that advantage.
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        move_val = 10**18
        for rx, ry in resources:
            ds_now = cheb(sx, sy, rx, ry)
            do_now = cheb(ox, oy, rx, ry)
            ds_new = cheb(nx, ny, rx, ry)

            # Lower is better:
            # - prefer smaller ds_new
            # - strongly prefer states where we are not losing the race
            # - slight tie-break toward denying if opponent is close
            lose_race = ds_new - ds_now  # change in our arrival time proxy
            deny = do_now - ds_new       # positive means we can arrive earlier than opponent from next pos
            v = ds_new
            if ds_new <= do_now:
                v -= 2.2 + 0.4 * max(0, deny)  # secure races
            else:
                v += 2.0 + 0.8 * (ds_new - do_now)  # avoid conceding
            v += 0.25 * lose_race
            v += 0.03 * cheb(nx, ny, sx, sy)  # mild stability

            if v < move_val:
                move_val = v

        if move_val < best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]